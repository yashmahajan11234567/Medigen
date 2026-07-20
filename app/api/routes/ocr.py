import logging
import time
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status

from app.auth.dependencies import get_current_active_user
from app.db.session import DbSession
from app.schemas.ocr import (
    OCRCompositionResponse,
    OCRDocumentResponse,
    OCRPharmacyBillResponse,
    ScanQualityDiagnosticsSchema,
)
from app.services.bill_parser import BillParser
from app.services.composition_parser import CompositionParser
from app.services.document_parser import DocumentParser
from app.services.generic_finder_service import GenericFinderService
from app.services.image_preprocessing import ImagePreprocessor
from app.services.ocr_service import OCRService
from app.services.paddleocr_engine import PaddleOCREngine
from app.services.text_cleaner import TextCleaner
from app.utils.ocr_utils import ImageQualityError, OCRError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ocr", tags=["ocr"])

# Shared service instances (stateless / can be shared across requests)
_ocr_engine = PaddleOCREngine()
_image_preprocessor = ImagePreprocessor()
_ocr_service = OCRService(engine=_ocr_engine, preprocessor=_image_preprocessor)
_text_cleaner = TextCleaner()
_composition_parser = CompositionParser()
_bill_parser = BillParser()
_document_parser = DocumentParser()


def _log_processing(
    request: Request,
    endpoint: str,
    duration_ms: int,
    ocr_confidence: float | None,
    success: bool,
) -> None:
    """Log OCR processing metadata.  NEVER log document content, patient
    names, or medicine names."""
    request_id = getattr(request.state, "request_id", str(uuid4()))
    logger.info(
        "OCR result | request_id=%s endpoint=%s duration_ms=%d ocr_confidence=%s success=%s",
        request_id,
        endpoint,
        duration_ms,
        f"{ocr_confidence:.2f}" if ocr_confidence is not None else "N/A",
        success,
    )


def _determine_mime_type(file: UploadFile) -> str:
    """Determine the MIME type of an uploaded file.

    Falls back to a reasonable guess based on filename extension if the
    client did not provide a Content-Type header.
    """
    if file.content_type and file.content_type != "application/octet-stream":
        return file.content_type

    filename = (file.filename or "").lower()
    ext_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".pdf": "application/pdf",
    }
    for ext, mime in ext_map.items():
        if filename.endswith(ext):
            return mime
    return "application/octet-stream"


def _build_quality_diagnostics(ocr_result) -> ScanQualityDiagnosticsSchema | None:
    """Build a ScanQualityDiagnosticsSchema from OCRResult quality data, if present."""
    if ocr_result.quality is None:
        return None
    return ScanQualityDiagnosticsSchema(
        issues=[i.value for i in ocr_result.quality.issues],
        blur_score=ocr_result.quality.blur_score,
        brightness=ocr_result.quality.brightness,
        contrast=ocr_result.quality.contrast,
        is_pass=ocr_result.quality.is_pass,
    )


def _handle_ocr_error(exc: Exception) -> None:
    """Map OCRService / parser exceptions to the appropriate HTTP error."""
    if isinstance(exc, ImageQualityError):
        if exc.code == "image_corrupted":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="The uploaded file appears to be corrupted or is not a valid image. "
                       "Please upload a valid PNG or JPEG image.",
            )
        if exc.code == "image_empty":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="The uploaded image appears to be empty or too small to process.",
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    msg = str(exc)
    if "mime" in msg.lower() or "unsupported" in msg.lower():
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Accepted types: PNG, JPEG.",
        )
    if "size" in msg.lower() and "large" in msg.lower():
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(exc),
        )
    if "empty" in msg.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty.",
        )
    if "confidence too low" in msg.lower():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    if isinstance(exc, OCRError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed. Please try again with a clearer image.",
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(exc),
    )


@router.post("/composition", response_model=OCRCompositionResponse)
async def ocr_composition(
    request: Request,
    db: DbSession,
    file: UploadFile = File(...),
    current_user=Depends(get_current_active_user),
) -> OCRCompositionResponse:
    """Extract a medicine composition from an image and search for generic substitutes.

    Pipeline: Upload → Validate → Quality Check → Preprocess → OCR → Clean →
              Composition Parser → Generic Finder → Response
    """
    start = time.perf_counter()
    endpoint = "composition"

    image_bytes = await file.read()
    mime_type = _determine_mime_type(file)

    try:
        ocr_result = _ocr_service.extract_bytes(image_bytes, mime_type)
    except (ValueError, ImageQualityError) as exc:
        _log_processing(request, endpoint, 0, None, False)
        _handle_ocr_error(exc)
    except OCRError as exc:
        _log_processing(request, endpoint, 0, None, False)
        _handle_ocr_error(exc)

    cleaned = _text_cleaner.clean(ocr_result.text)
    if not cleaned:
        _log_processing(request, endpoint, 0, ocr_result.average_confidence, False)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No text could be extracted from the image. "
                   "Please ensure the image shows a medicine label clearly.",
        )

    try:
        composition = _composition_parser.parse(cleaned)
    except (ValueError, Exception) as exc:
        _log_processing(request, endpoint, 0, ocr_result.average_confidence, False)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not parse medicine composition from the extracted text. "
                   f"Please verify the image shows a single medicine clearly.",
        )

    try:
        generic_finder = GenericFinderService(db)
        search_result = generic_finder.scan_by_composition(composition)
    except Exception:
        _log_processing(request, endpoint, 0, ocr_result.average_confidence, False)
        raise

    duration_ms = int((time.perf_counter() - start) * 1000)
    _log_processing(request, endpoint, duration_ms, ocr_result.average_confidence, True)

    return OCRCompositionResponse(
        ocr_confidence=ocr_result.average_confidence,
        quality_diagnostics=_build_quality_diagnostics(ocr_result),
        processing_time_ms=duration_ms,
        result=search_result,
    )


@router.post("/pharmacy-bill", response_model=OCRPharmacyBillResponse)
async def ocr_pharmacy_bill(
    request: Request,
    file: UploadFile = File(...),
    current_user=Depends(get_current_active_user),
) -> OCRPharmacyBillResponse:
    """Parse a pharmacy bill image and return structured medicine entries.

    Pipeline: Upload → Validate → Quality Check → Preprocess → OCR → Clean →
              BillParser → Response

    NOTE: This endpoint does NOT write to the database or interact with
    Scheduler / Inventory modules.  Use the /api/v1/schedule/from-bill and
    /api/v1/inventory endpoints for that.
    """
    start = time.perf_counter()
    endpoint = "pharmacy-bill"

    image_bytes = await file.read()
    mime_type = _determine_mime_type(file)

    try:
        ocr_result = _ocr_service.extract_bytes(image_bytes, mime_type)
    except (ValueError, ImageQualityError) as exc:
        _log_processing(request, endpoint, 0, None, False)
        _handle_ocr_error(exc)
    except OCRError as exc:
        _log_processing(request, endpoint, 0, None, False)
        _handle_ocr_error(exc)

    cleaned = _text_cleaner.clean(ocr_result.text)
    if not cleaned:
        _log_processing(request, endpoint, 0, ocr_result.average_confidence, False)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No text could be extracted from the image. "
                   "Please ensure the image shows a pharmacy bill clearly.",
        )

    try:
        bill_result = _bill_parser.parse(cleaned)
    except (ValueError, Exception) as exc:
        _log_processing(request, endpoint, 0, ocr_result.average_confidence, False)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not parse medicine entries from the bill text. "
                   f"Please ensure the bill image is clear and readable.",
        )

    duration_ms = int((time.perf_counter() - start) * 1000)
    _log_processing(request, endpoint, duration_ms, ocr_result.average_confidence, True)

    return OCRPharmacyBillResponse(
        ocr_confidence=ocr_result.average_confidence,
        quality_diagnostics=_build_quality_diagnostics(ocr_result),
        processing_time_ms=duration_ms,
        result=bill_result,
    )


@router.post("/document", response_model=OCRDocumentResponse)
async def ocr_document(
    request: Request,
    file: UploadFile = File(...),
    current_user=Depends(get_current_active_user),
) -> OCRDocumentResponse:
    """Parse a medical document image and return structured metadata.

    Pipeline: Upload → Validate → Quality Check → Preprocess → OCR → Clean →
              DocumentParser → Response

    Recognised document types: Prescription, Pharmacy Bill, Blood Test Report,
    Laboratory Report, Diagnostic Report, Discharge Summary, Medical Certificate, Other.

    NOTE: The parser extracts available fields and NEVER infers missing values.
    This endpoint does NOT perform diagnosis, treatment recommendations,
    or any clinical decision-making.
    """
    start = time.perf_counter()
    endpoint = "document"

    # Read file content
    image_bytes = await file.read()
    mime_type = _determine_mime_type(file)
    original_filename = file.filename or "upload"

    # Prepare upload directory
    from pathlib import Path
    import os
    import mimetypes
    from uuid import uuid4

    UPLOAD_DIR = Path("uploads/medical_records")
    try:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not create upload directory: {e}",
        )

    # Determine file extension
    _, ext = os.path.splitext(original_filename)
    if not ext:
        # Guess extension from mimetype
        ext = mimetypes.guess_extension(mime_type) or ".bin"
    # Generate unique filename to avoid collisions
    unique_filename = f"{uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / unique_filename

    # Save file to disk
    try:
        with open(file_path, "wb") as f:
            f.write(image_bytes)
    except IOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {e}",
        )

    # Prepare file metadata for response
    storage_path = str(f"uploads/medical_records/{unique_filename}")
    file_size = len(image_bytes)

    try:
        ocr_result = _ocr_service.extract_bytes(image_bytes, mime_type)
    except (ValueError, ImageQualityError) as exc:
        _log_processing(request, endpoint, 0, None, False)
        _handle_ocr_error(exc)
    except OCRError as exc:
        _log_processing(request, endpoint, 0, None, False)
        _handle_ocr_error(exc)

    cleaned = _text_cleaner.clean(ocr_result.text)
    if not cleaned:
        _log_processing(request, endpoint, 0, ocr_result.average_confidence, False)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No text could be extracted from the image. "
                   "Please ensure the document image is clear and readable.",
        )

    try:
        doc_result = _document_parser.parse(cleaned)
    except (ValueError, Exception) as exc:
        _log_processing(request, endpoint, 0, ocr_result.average_confidence, False)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not parse document information from the extracted text. "
                   f"Please ensure the document image is clear and readable.",
        )

    duration_ms = int((time.perf_counter() - start) * 1000)
    _log_processing(request, endpoint, duration_ms, ocr_result.average_confidence, True)

    return OCRDocumentResponse(
        ocr_confidence=ocr_result.average_confidence,
        quality_diagnostics=_build_quality_diagnostics(ocr_result),
        processing_time_ms=duration_ms,
        result=doc_result,
        storage_path=storage_path,
        file_name=original_filename,
        file_type=mime_type,
        file_size=file_size,
    )