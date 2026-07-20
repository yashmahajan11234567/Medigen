from typing import Optional

from pydantic import BaseModel

from app.schemas.bill_parser import BillParseResult
from app.schemas.document_parser import DocumentParseResult
from app.schemas.generic_finder import GenericFinderSearchResponse


class ScanQualityDiagnosticsSchema(BaseModel):
    """Quality assessment of the uploaded scan/image, serialised for API responses."""

    issues: list[str] = []
    blur_score: Optional[float] = None
    brightness: Optional[float] = None
    contrast: Optional[float] = None
    is_pass: bool = True


class OCRCompositionResponse(BaseModel):
    """Response from the /ocr/composition endpoint.

    Fields:
        ocr_confidence: Mean confidence of the OCR engine (0-1).
        quality_diagnostics: Quality assessment of the source image, if available.
        processing_time_ms: Total server-side processing time in milliseconds.
        result: Results of the generic medicine search.
    """

    ocr_confidence: Optional[float] = None
    quality_diagnostics: Optional[ScanQualityDiagnosticsSchema] = None
    processing_time_ms: int
    result: GenericFinderSearchResponse


class OCRPharmacyBillResponse(BaseModel):
    """Response from the /ocr/pharmacy-bill endpoint."""

    ocr_confidence: Optional[float] = None
    quality_diagnostics: Optional[ScanQualityDiagnosticsSchema] = None
    processing_time_ms: int
    result: BillParseResult


class OCRDocumentResponse(BaseModel):
    """Response from the /ocr/document endpoint."""

    ocr_confidence: Optional[float] = None
    quality_diagnostics: Optional[ScanQualityDiagnosticsSchema] = None
    processing_time_ms: int
    result: DocumentParseResult
    storage_path: str | None = None
    file_name: str | None = None
    file_type: str | None = None
    file_size: int | None = None