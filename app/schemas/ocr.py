from pydantic import BaseModel

from app.schemas.bill_parser import BillParseResult
from app.schemas.document_parser import DocumentParseResult
from app.schemas.generic_finder import GenericFinderSearchResponse


class OCRCompositionResponse(BaseModel):
    ocr_confidence: float | None = None
    processing_time_ms: int
    result: GenericFinderSearchResponse


class OCRPharmacyBillResponse(BaseModel):
    ocr_confidence: float | None = None
    processing_time_ms: int
    result: BillParseResult


class OCRDocumentResponse(BaseModel):
    ocr_confidence: float | None = None
    processing_time_ms: int
    result: DocumentParseResult