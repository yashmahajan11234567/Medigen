import pytest
from app.schemas.document_parser import DocumentParseResult, DocumentType
from app.services.document_parser import DocumentParser


class TestDocumentParser:
    def setup_method(self):
        self.parser = DocumentParser()

    # ── document type detection ─────────────────────────────────────

    def test_prescription(self):
        """Detect a prescription document."""
        text = (
            "Prescription\n"
            "Patient: John Doe\n"
            "Dr. Smith\n"
            "Date: 12/05/2026\n"
            "\n"
            "Paracetamol 500 mg\n"
            "Amoxicillin 250 mg"
        )
        result = self.parser.parse(text)
        assert result.document_type == DocumentType.PRESCRIPTION
        assert result.patient_name == "John Doe"
        assert result.doctor_name is not None

    def test_pharmacy_bill(self):
        """Detect a pharmacy bill document."""
        text = (
            "Pharmacy Bill\n"
            "Bill No: 12345\n"
            "Paracetamol 500 mg\n"
            "Qty 10\n"
            "Total Amount: 50.00"
        )
        result = self.parser.parse(text)
        assert result.document_type == DocumentType.PHARMACY_BILL

    def test_blood_test_report(self):
        """Detect a blood test report."""
        text = (
            "Blood Test Report\n"
            "Patient: Jane Doe\n"
            "Date: 2026-05-12\n"
            "\n"
            "Hemoglobin: 14.5 g/dL\n"
            "WBC: 7500 /uL\n"
            "Platelet: 250000 /uL"
        )
        result = self.parser.parse(text)
        assert result.document_type == DocumentType.BLOOD_TEST_REPORT

    def test_laboratory_report(self):
        """Detect a laboratory report."""
        text = (
            "Laboratory Report\n"
            "Lab No: L20260512\n"
            "Patient: John Doe\n"
            "Specimen: Blood\n"
            "Test Name: Lipid Profile\n"
            "Reference Range: See below"
        )
        result = self.parser.parse(text)
        assert result.document_type == DocumentType.LABORATORY_REPORT

    def test_diagnostic_report(self):
        """Detect a diagnostic report."""
        text = (
            "Diagnostic Report\n"
            "Patient: John Doe\n"
            "Ultrasound Abdomen\n"
            "Findings: Normal"
        )
        result = self.parser.parse(text)
        assert result.document_type == DocumentType.DIAGNOSTIC_REPORT

    def test_discharge_summary(self):
        """Detect a discharge summary."""
        text = (
            "Discharge Summary\n"
            "Patient: John Doe\n"
            "Date of Admission: 10/05/2026\n"
            "Date of Discharge: 12/05/2026\n"
            "Condition on Discharge: Stable"
        )
        result = self.parser.parse(text)
        assert result.document_type == DocumentType.DISCHARGE_SUMMARY

    def test_medical_certificate(self):
        """Detect a medical certificate."""
        text = (
            "Medical Certificate\n"
            "Patient: John Doe\n"
            "This is to certify that Mr. John Doe is medically fit\n"
            "Sick leave recommended for 3 days"
        )
        result = self.parser.parse(text)
        assert result.document_type == DocumentType.MEDICAL_CERTIFICATE

    def test_unknown_document(self):
        """Default to OTHER for unrecognised document types."""
        text = (
            "Shopping List\n"
            "Milk\n"
            "Eggs\n"
            "Bread"
        )
        result = self.parser.parse(text)
        assert result.document_type == DocumentType.OTHER

    # ── field extraction ────────────────────────────────────────────

    def test_patient_name_extracted(self):
        """Extract patient name from labelled field."""
        text = "Patient: Alice Wonderland\nDate: 12/05/2026"
        result = self.parser.parse(text)
        assert result.patient_name == "Alice Wonderland"

    def test_doctor_name_extracted(self):
        """Extract doctor name from labelled field."""
        text = "Doctor: Dr. House\nPatient: John Doe"
        result = self.parser.parse(text)
        assert result.doctor_name == "Dr. House"

    def test_hospital_name_extracted(self):
        """Extract hospital or lab name."""
        text = "Hospital: City Medical Center\nPatient: John Doe"
        result = self.parser.parse(text)
        assert result.hospital_or_lab == "City Medical Center"

    def test_missing_fields(self):
        """Return None for absent fields."""
        text = "Some random text without any labelled fields"
        result = self.parser.parse(text)
        assert result.patient_name is None
        assert result.doctor_name is None
        assert result.hospital_or_lab is None
        assert result.report_date is None
        assert result.diagnosis_text is None
        assert result.notes is None

    def test_diagnosis_extracted(self):
        """Extract diagnosis text from labelled field."""
        text = "Diagnosis: Acute Bronchitis\nPatient: John Doe"
        result = self.parser.parse(text)
        assert result.diagnosis_text == "Acute Bronchitis"

    def test_notes_extracted(self):
        """Extract notes from labelled field."""
        text = "Notes: Follow up in 2 weeks\nPatient: John Doe"
        result = self.parser.parse(text)
        assert result.notes == "Follow up in 2 weeks"

    # ── medicine extraction ─────────────────────────────────────────

    def test_single_medicine(self):
        """Extract a single medicine from document text."""
        text = "Prescription\nPatient: John Doe\nParacetamol 500 mg\nQty 10"
        result = self.parser.parse(text)
        assert len(result.medicines) == 1
        assert result.medicines[0].medicine_name == "Paracetamol"
        assert result.medicines[0].strength == "500"
        assert result.medicines[0].dosage_unit == "mg"

    def test_multiple_medicines(self):
        """Extract multiple medicines preserving order."""
        text = (
            "Prescription\n"
            "Patient: John Doe\n"
            "Amoxicillin 250 mg\n"
            "Ibuprofen 400 mg\n"
            "Cetirizine 10 mg"
        )
        result = self.parser.parse(text)
        assert len(result.medicines) == 3
        assert result.medicines[0].medicine_name == "Amoxicillin"
        assert result.medicines[1].medicine_name == "Ibuprofen"
        assert result.medicines[2].medicine_name == "Cetirizine"

    def test_medicines_deduped(self):
        """Deduplicate same medicine appearing multiple times."""
        text = (
            "Prescription\n"
            "Patient: John Doe\n"
            "Paracetamol 500 mg\n"
            "Paracetamol 500 mg"
        )
        result = self.parser.parse(text)
        assert len(result.medicines) == 1
        assert result.medicines[0].medicine_name == "Paracetamol"

    def test_no_medicines(self):
        """Return empty list when no medicines are found."""
        text = "Patient: John Doe\nDiagnosis: Cold"
        result = self.parser.parse(text)
        assert result.medicines == []

    # ── date parsing ────────────────────────────────────────────────

    def test_date_dd_mm_yyyy_slash(self):
        """Parse DD/MM/YYYY format."""
        text = "Patient: John Doe\nDate: 12/05/2026"
        result = self.parser.parse(text)
        assert result.report_date == "2026-05-12"

    def test_date_dd_mm_yyyy_hyphen(self):
        """Parse DD-MM-YYYY format."""
        text = "Patient: John Doe\nDate: 12-05-2026"
        result = self.parser.parse(text)
        assert result.report_date == "2026-05-12"

    def test_date_yyyy_mm_dd(self):
        """Parse YYYY-MM-DD format."""
        text = "Patient: John Doe\nDate: 2026-05-12"
        result = self.parser.parse(text)
        assert result.report_date == "2026-05-12"

    def test_date_dd_month_yyyy(self):
        """Parse 'DD Month YYYY' format."""
        text = "Patient: John Doe\nDate: 12 May 2026"
        result = self.parser.parse(text)
        assert result.report_date == "2026-05-12"

    def test_date_month_variants(self):
        """Parse month name abbreviations."""
        text = "Patient: John Doe\nDate: 5 Jan 2026"
        result = self.parser.parse(text)
        assert result.report_date == "2026-01-05"

        text = "Patient: John Doe\nDate: 15 Dec 2025"
        result = self.parser.parse(text)
        assert result.report_date == "2025-12-15"

    def test_invalid_date(self):
        """Return None for invalid dates."""
        text = "Patient: John Doe\nDate: 32/01/2026"
        result = self.parser.parse(text)
        assert result.report_date is None

    def test_invalid_date_month(self):
        """Return None when month is out of range."""
        text = "Patient: John Doe\nDate: 13/13/2026"
        result = self.parser.parse(text)
        assert result.report_date is None

    # ── empty input ─────────────────────────────────────────────────

    def test_empty_input(self):
        """Reject empty text."""
        with pytest.raises(ValueError, match="Empty or whitespace-only input"):
            self.parser.parse("")

    def test_whitespace_only_input(self):
        """Reject whitespace-only text."""
        with pytest.raises(ValueError, match="Empty or whitespace-only input"):
            self.parser.parse("   \n  \t  ")

    # ── unicode text ────────────────────────────────────────────────

    def test_unicode_text(self):
        """Handle text with non-ASCII characters."""
        text = (
            "Prescription\n"
            "Patient: José García\n"
            "Doctor: Dr. Müller\n"
            "Date: 12/05/2026\n"
            "\n"
            "Paracetamol 500 mg"
        )
        result = self.parser.parse(text)
        assert result.patient_name == "José García"
        assert result.doctor_name == "Dr. Müller"
        assert len(result.medicines) == 1

    def test_unicode_diagnosis(self):
        """Handle diagnosis text with accented characters."""
        text = "Diagnosis: Infection respiratoire aiguë\nPatient: Jean"
        result = self.parser.parse(text)
        assert result.diagnosis_text == "Infection respiratoire aiguë"

    # ── OCR-cleaned input ───────────────────────────────────────────

    def test_ocr_cleaned_prescription(self):
        """Parse text resembling OCR output from a prescription."""
        text = (
            "Prescription\n"
            "Patient: John Doe\n"
            "Dr. Smith\n"
            "Date:12/05/2026\n"
            "\n"
            "Tab Paracetamol 500 mg\n"
            "Cap Amoxicillin 250 mg"
        )
        result = self.parser.parse(text)
        assert result.document_type == DocumentType.PRESCRIPTION
        assert result.patient_name == "John Doe"
        assert len(result.medicines) == 2

    def test_ocr_variable_spacing(self):
        """Handle irregular spacing typical of OCR output."""
        text = (
            "Patient:  John   Doe\n"
            "Date:   12/05/2026\n"
            "Paracetamol   500  mg"
        )
        result = self.parser.parse(text)
        assert result.patient_name == "John Doe"
        assert result.report_date == "2026-05-12"
        assert len(result.medicines) == 1

    # ── raw text preservation ───────────────────────────────────────

    def test_raw_text_preserved(self):
        """Verify raw_text matches the input."""
        text = "Patient: John Doe\nDate: 12/05/2026"
        result = self.parser.parse(text)
        assert result.raw_text == text.strip()

    # ── doctor_name field examples from requirements ────────────────

    def test_doctor_various_formats(self):
        """Handle various doctor name label formats."""
        text = "Dr. Sarah Connor\nPatient: John\nDate: 12/05/2026"
        result = self.parser.parse(text)
        assert result.doctor_name == "Sarah Connor"

        text = "Physician: Dr. House\nPatient: John"
        result = self.parser.parse(text)
        assert result.doctor_name == "Dr. House"

    # ── hospital/lab extraction ─────────────────────────────────────

    def test_lab_name_extracted(self):
        """Extract lab name from lab report."""
        text = "Laboratory Report\nLab: Metropolis Lab\nPatient: John"
        result = self.parser.parse(text)
        assert result.hospital_or_lab == "Metropolis Lab"

    # ── edge cases ─────────────────────────────────────────────────

    def test_date_with_ordinal_suffix(self):
        """Parse dates with ordinal suffixes like '1st'."""
        text = "Patient: John\nDate: 1st January 2024"
        result = self.parser.parse(text)
        assert result.report_date == "2024-01-01"

    def test_no_document_type_keywords(self):
        """No type keywords should result in OTHER."""
        text = "Patient: John\nJust some notes here"
        result = self.parser.parse(text)
        assert result.document_type == DocumentType.OTHER
        assert result.patient_name == "John"

    def test_mixed_document_type_keywords(self):
        """When mixed keywords exist, the highest-scoring type wins."""
        text = (
            "Prescription\n"
            "Rx\n"
            "Date: 12/05/2026\n"
            "Patient: John\n"
            "Paracetamol 500 mg"
        )
        result = self.parser.parse(text)
        assert result.document_type == DocumentType.PRESCRIPTION


if __name__ == "__main__":
    pytest.main([__file__, "-v"])