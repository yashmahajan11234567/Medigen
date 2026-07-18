from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.bill_parser import MedicineEntry


class DocumentType(StrEnum):
    PRESCRIPTION = "prescription"
    PHARMACY_BILL = "pharmacy_bill"
    BLOOD_TEST_REPORT = "blood_test_report"
    LABORATORY_REPORT = "laboratory_report"
    DIAGNOSTIC_REPORT = "diagnostic_report"
    DISCHARGE_SUMMARY = "discharge_summary"
    MEDICAL_CERTIFICATE = "medical_certificate"
    OTHER = "other"


class DocumentParseResult(BaseModel):
    """Structured result from parsing a medical document."""

    document_type: DocumentType
    patient_name: str | None = None
    doctor_name: str | None = None
    hospital_or_lab: str | None = None
    report_date: str | None = None
    medicines: list[MedicineEntry] = Field(default_factory=list)
    diagnosis_text: str | None = None
    notes: str | None = None
    raw_text: str