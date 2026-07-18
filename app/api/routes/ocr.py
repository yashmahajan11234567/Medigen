import logging
import time
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status

from app.db.session import DbSession
from app.schemas.ocr import OCRCompositionResponse, OCRDocumentResponse, OCRPharmacyBillResponse
from app.services.bill_parser import BillParser
from app.services.composition_parser import CompositionParser
from app.services.document_parser import DocumentParser
from app.services.generic_finder_service import GenericFinderService
from app.services.ocr_service import OCRService
from app.services.paddleocr_engine import PaddleOCREngine
from app.services.text_cleaner import TextCleaner
from app.utils.ocr_utils import OCRError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ocr", tags=["ocr"])

# Shared service instances (stateless / can be shared across requests)
_ocr_engine = PaddleOCREngine()
_ocr_service = OCRService(engine=_ocr_engine)
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


def _handle_ocr_error(exc: ValueError) -> None:
    """Map OCRService ValueError to the appropriate HTTP error."""
    msg = str(exc)
    if "mime type" in msg.lower() or "mime" in msg.lower():
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=msg)
    if "size" in msg.lower() and "large" in msg.lower():
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=msg)
    if "empty" in msg.lower():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


@router.post("/composition", response_model=OCRCompositionResponse)
async def ocr_composition(
    request: Request,
    db: DbSession,
    file: UploadFile = File(...),
) -> OCRCompositionResponse:
    start = time.perf_counter()
    endpoint = "composition"

    image_bytes = await file.read()
    mime_type = _determine_mime_type(file)

    try:
        ocr_result = _ocr_service.extract_bytes(image_bytes, mime_type)
    except ValueError as exc:
        _log_processing(request, endpoint, 0, None, False)
        _handle_ocr_error(exc)
    except OCRError as exc:
        _log_processing(request, endpoint, 0, None, False)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {exc}",
        )

    cleaned = _text_cleaner.clean(ocr_result.text)
    if not cleaned:
        _log_processing(request, endpoint, 0, ocr_result.average_confidence, False)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="OCR returned empty text after cleaning",
        )

    try:
        composition = _composition_parser.parse(cleaned)
    except (ValueError, Exception) as exc:
        _log_processing(request, endpoint, 0, ocr_result.average_confidence, False)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Composition parsing failed: {exc}",
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
        processing_time_ms=duration_ms,
        result=search_result,
    )


@router.post("/pharmacy-bill", response_model=OCRPharmacyBillResponse)
async def ocr_pharmacy_bill(
    request: Request,
    file: UploadFile = File(...),
) -> OCRPharmacyBillResponse:
    """Parse a pharmacy bill image and return structured medicine entries.

    Pipeline: Upload → Validate → OCR → Clean → BillParser → Response

    NOTE: This endpoint is preview-only.  It does NOT write to the database
    or interact with Scheduler / Inventory modules.
    """
    start = time.perf_counter()
    endpoint = "pharmacy-bill"

    image_bytes = await file.read()
    mime_type = _determine_mime_type(file)

    try:
        ocr_result = _ocr_service.extract_bytes(image_bytes, mime_type)
    except ValueError as exc:
        _log_processing(request, endpoint, 0, None, False)
        _handle_ocr_error(exc)
    except OCRError as exc:
        _log_processing(request, endpoint, 0, None, False)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {exc}",
        )

    cleaned = _text_cleaner.clean(ocr_result.text)
    if not cleaned:
        _log_processing(request, endpoint, 0, ocr_result.average_confidence, False)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="OCR returned empty text after cleaning",
        )

    try:
        bill_result = _bill_parser.parse(cleaned)
    except (ValueError, Exception) as exc:
        _log_processing(request, endpoint, 0, ocr_result.average_confidence, False)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Bill parsing failed: {exc}",
        )

    duration_ms = int((time.perf_counter() - start) * 1000)
    _log_processing(request, endpoint, duration_ms, ocr_result.average_confidence, True)

    return OCRPharmacyBillResponse(
        ocr_confidence=ocr_result.average_confidence,
        processing_time_ms=duration_ms,
        result=bill_result,
    )


@router.post("/document", response_model=OCRDocumentResponse)
async def ocr_document(
    request: Request,
    file: UploadFile = File(...),
) -> OCRDocumentResponse:
    """Parse a medical document image and return structured metadata.

    Pipeline: Upload → Validate → OCR → Clean → DocumentParser → Response

    Recognised document types: Prescription, Pharmacy Bill, Blood Test Report,
    Laboratory Report, Diagnostic Report, Discharge Summary, Medical Certificate, Other.

    NOTE: The parser extracts available fields and NEVER infers missing values.
    This endpoint does NOT perform diagnosis, treatment recommendations,
    or any clinical decision-making.
    """
    start = time.perf_counter()
    endpoint = "document"

    image_bytes = await file.read()
    mime_type = _determine_mime_type(file)

    try:
        ocr_result = _ocr_service.extract_bytes(image_bytes, mime_type)
    except ValueError as exc:
        _log_processing(request, endpoint, 0, None, False)
        _handle_ocr_error(exc)
    except OCRError as exc:
        _log_processing(request, endpoint, 0, None, False)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {exc}",
        )

    cleaned = _text_cleaner.clean(ocr_result.text)
    if not cleaned:
        _log_processing(request, endpoint, 0, ocr_result.average_confidence, False)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="OCR returned empty text after cleaning",
        )

    try:
        doc_result = _document_parser.parse(cleaned)
    except (ValueError, Exception) as exc:
        _log_processing(request, endpoint, 0, ocr_result.average_confidence, False)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Document parsing failed: {exc}",
        )

    duration_ms = int((time.perf_counter() - start) * 1000)
    _log_processing(request, endpoint, duration_ms, ocr_result.average_confidence, True)

    return OCRDocumentResponse(
        ocr_confidence=ocr_result.average_confidence,
        processing_time_ms=duration_ms,
        result=doc_result,
    )