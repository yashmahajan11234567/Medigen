import re
from datetime import datetime

from app.core.exceptions import AppException
from app.schemas.bill_parser import MedicineEntry
from app.schemas.document_parser import DocumentParseResult, DocumentType
from app.services.composition_parser import CompositionParser


MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

# Each keyword is weighted: stronger matches have higher weights.
# The type with the highest total weight wins.
DOCUMENT_KEYWORDS: dict[DocumentType, dict[str, int]] = {
    DocumentType.PRESCRIPTION: {
        "prescription": 10,
        "rx": 8,
        "take": 2,
        "dispense": 4,
        "refill": 4,
        "sig": 3,
    },
    DocumentType.PHARMACY_BILL: {
        "pharmacy bill": 10,
        "receipt": 6,
        "gst": 5,
        "invoice": 6,
        "mrp": 4,
        "bill no": 5,
        "total amount": 3,
        "qty": 3,
    },
    DocumentType.BLOOD_TEST_REPORT: {
        "complete blood count": 10,
        "cbc": 8,
        "hemoglobin": 6,
        "blood test": 8,
        "wbc": 5,
        "rbc": 5,
        "platelet": 5,
        "lipid profile": 8,
        "blood sugar": 5,
        "hba1c": 5,
        "fasting": 3,
        "cholesterol": 4,
        "triglyceride": 4,
    },
    DocumentType.LABORATORY_REPORT: {
        "laboratory": 8,
        "lab report": 8,
        "specimen": 6,
        "reference range": 6,
        "lab no": 5,
        "test name": 4,
        "collected on": 4,
        "reported on": 4,
    },
    DocumentType.DIAGNOSTIC_REPORT: {
        "diagnostic": 8,
        "radiology": 8,
        "x-ray": 6,
        "xray": 6,
        "ultrasound": 6,
        "ct scan": 6,
        "mri": 6,
        "ecg": 5,
        "echo": 5,
        "imaging": 4,
        "sonography": 5,
    },
    DocumentType.DISCHARGE_SUMMARY: {
        "discharge summary": 10,
        "discharge date": 8,
        "discharged": 6,
        "admission": 5,
        "condition on discharge": 8,
        "hospital stay": 4,
        "date of admission": 6,
        "date of discharge": 6,
    },
    DocumentType.MEDICAL_CERTIFICATE: {
        "medical certificate": 10,
        "certificate of fitness": 10,
        "medically fit": 8,
        "certify": 6,
        "sick leave": 6,
        "fitness certificate": 8,
    },
}


class DocumentParser:
    """Parse cleaned OCR text from medical documents into structured metadata.

    Supports document types:
      - Prescription
      - Pharmacy Bill
      - Blood Test Report
      - Laboratory Report
      - Diagnostic Report
      - Discharge Summary
      - Medical Certificate
      - Other (default)

    Extracts available fields using label-based patterns.
    Never infers or guesses missing values.
    """

    def __init__(self) -> None:
        self._composition_parser = CompositionParser()

    # ── public entry point ──────────────────────────────────────────

    def parse(self, raw_text: str) -> DocumentParseResult:
        """Transform cleaned OCR document text into a DocumentParseResult.

        Args:
            raw_text: Cleaned text extracted by OCR.

        Returns:
            DocumentParseResult with detected type, extracted fields,
            and medicine entries.

        Raises:
            ValueError: For empty or whitespace-only input.
        """
        if not raw_text or not raw_text.strip():
            raise ValueError("Empty or whitespace-only input")

        text = raw_text.strip()
        lines = [line.strip() for line in text.split("\n")]

        doc_type = self._detect_document_type(text)
        patient_name = self._extract_field(lines, self._patient_patterns())
        doctor_name = self._extract_field(lines, self._doctor_patterns())
        hospital_or_lab = self._extract_field(lines, self._hospital_patterns())
        report_date = self._extract_date(lines)
        medicines = self._parse_medicines(lines)
        diagnosis_text = self._extract_field(lines, self._diagnosis_patterns())
        notes = self._extract_field(lines, self._notes_patterns())

        return DocumentParseResult(
            document_type=doc_type,
            patient_name=patient_name,
            doctor_name=doctor_name,
            hospital_or_lab=hospital_or_lab,
            report_date=report_date,
            medicines=medicines,
            diagnosis_text=diagnosis_text,
            notes=notes,
            raw_text=text,
        )

    # ── document type detection ─────────────────────────────────────

    def _detect_document_type(self, text: str) -> DocumentType:
        """Detect document type using weighted keyword matching."""
        lower = text.lower()
        scores: dict[DocumentType, int] = {}

        for doc_type, keywords in DOCUMENT_KEYWORDS.items():
            total = 0
            for keyword, weight in keywords.items():
                if keyword in lower:
                    total += weight
            if total > 0:
                scores[doc_type] = total

        if not scores:
            return DocumentType.OTHER

        return max(scores, key=scores.get)  # type: ignore[type-var]

    # ── field extraction patterns ───────────────────────────────────

    @staticmethod
    def _patient_patterns() -> list[str]:
        return [
            r"(?i)^patient\s*(?:name)?\s*[:.]\s*(.+)",
            r"(?i)^patient\s*[:.]\s*(.+)",
            r"(?i)^name\s*[:.]\s*(.+?)(?:\s+(?:age|sex|male|female|m|f)(?:\s|$))",
        ]

    @staticmethod
    def _doctor_patterns() -> list[str]:
        return [
            r"(?i)^(?:doctor|dr\.?|physician)\s*(?:name)?\s*[:.]\s*(.+)",
            r"(?i)^(?:consultant|referring)\s*(?:doctor|physician)?\s*[:.]\s*(.+)",
        ]

    @staticmethod
    def _hospital_patterns() -> list[str]:
        return [
            r"(?i)^(?:hospital|healthcare|medical center|medical centre|clinic|lab|laboratory)\s*(?:name)?\s*[:.]\s*(.+)",
            r"(?i)^(?:facility|institution)\s*[:.]\s*(.+)",
        ]

    @staticmethod
    def _diagnosis_patterns() -> list[str]:
        return [
            r"(?i)^(?:diagnosis|diagnostic|impression|assessment)\s*[:.]\s*(.+)",
            r"(?i)^(?:findings|conclusion)\s*[:.]\s*(.+)",
        ]

    @staticmethod
    def _notes_patterns() -> list[str]:
        return [
            r"(?i)^(?:notes?|remarks?|comments?|additional\s*(?:notes?)?)\s*[:.]\s*(.+)",
            r"(?i)^(?:instructions?|recommendations?)\s*[:.]\s*(.+)",
        ]

    # ── field extraction ────────────────────────────────────────────

    @staticmethod
    def _extract_field(lines: list[str], patterns: list[str]) -> str | None:
        """Extract a field value from document lines using the given patterns.

        Returns the first match found across all lines.
        """
        for line in lines:
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    value = match.group(1).strip().rstrip(".")
                    if value:
                        # Normalise internal whitespace
                        return re.sub(r"\s+", " ", value)
        return None

    # ── medicine extraction ─────────────────────────────────────────

    def _parse_medicines(self, lines: list[str]) -> list[MedicineEntry]:
        """Extract medicine entries from document lines.

        Uses CompositionParser as the primary parser, with a fallback
        regex-based extraction for lines that don't match the strict
        5-field composition format.
        """
        medicines: list[MedicineEntry] = []
        seen: set[str] = set()

        for line in lines:
            entry = self._extract_single_medicine(line)
            if entry is None:
                continue
            key = entry.medicine_name.lower().strip()
            if key not in seen:
                seen.add(key)
                medicines.append(entry)

        return medicines

    def _extract_single_medicine(self, line: str) -> MedicineEntry | None:
        """Try to extract a medicine entry from a single line."""
        cleaned = self._strip_dosage_instructions(line)
        if not cleaned:
            return None

        if self._is_non_medicine_line(cleaned):
            return None

        # Primary: CompositionParser
        try:
            result = self._composition_parser.parse(cleaned)
            return MedicineEntry(
                medicine_name=result.ingredient,
                strength=result.strength,
                dosage_unit=result.unit,
            )
        except (ValueError, AppException):
            pass

        # Fallback: simple name + strength + optional unit
        return self._extract_name_strength(cleaned)

    # ── helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _strip_dosage_instructions(line: str) -> str:
        """Remove trailing dosage instructions from a medicine line.

        E.g. 'Paracetamol 500 mg - 1 tab TDS' → 'Paracetamol 500 mg'
        """
        cleaned = re.sub(
            r"\s*[-–]\s*\d+\s+\w+(?:\s+\w+)?\s*$", "", line
        )
        cleaned = re.sub(
            r"\s+\d+\s+(?:tab|tabs|cap|caps|inj|ml|mg|drop|drops)\s+\w+\s*$",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(
            r"\s+\d+[-–]\d+[-–]\d+\s*$", "", cleaned
        )
        return cleaned.strip()

    @staticmethod
    def _is_non_medicine_line(line: str) -> bool:
        """Check if a line is clearly not a medicine entry."""
        # Skip lines that look like labels, headers, or instructions
        non_medicine_patterns = [
            r"(?i)^(?:patient|doctor|dr|hospital|lab|date|diagnosis|notes|remarks|"
            r"prescription|dispense|refill|sig|take|qty|quantity|mrp|rate|total|"
            r"gst|bill|invoice|receipt|blood|hemoglobin|wbc|rbc|platelet|"
            r"cholesterol|triglyceride|fasting|specimen|test name|reference|"
            r"laboratory|ultrasound|x-ray|xray|mri|ct scan|ecg|echo|"
            r"admission|discharge|condition|admitted|"
            r"certify|certificate|medically|"
            r"page|print|report|result|unit|collected|reported|age|sex|male|female)"
            r"[\s:]",
        ]
        for pattern in non_medicine_patterns:
            if re.match(pattern, line):
                return True
        return False

    @staticmethod
    def _extract_name_strength(line: str) -> MedicineEntry | None:
        """Fallback: extract medicine name + strength + optional unit.

        Handles:
          - 'Paracetamol 500 mg'         → name, strength='500',   unit='mg'
          - 'Crocin 650'                 → name, strength='650',   unit=None
          - 'Tab Paracetamol 500 mg'     → (prefix stripped)       unit='mg'
        """
        # Strip common dosage-form prefixes
        cleaned = re.sub(
            r"^(tab\.?|tabs?\.?|cap\.?|caps?\.?|inj\.?|syp\.?|susp\.?|"
            r"oint\.?|cream|drops?|lot\.?|solution|gel|inhaler)\s+",
            "",
            line,
            flags=re.IGNORECASE,
        )

        # Name(s) Strength Unit
        match = re.match(
            r"^([A-Za-z][A-Za-z\s\-'.]+?)\s+"
            r"(\d+(?:\.\d+)?)\s+"
            r"([a-zA-Z/%]\S*)(?:\s|$)",
            cleaned,
        )
        if match:
            name = match.group(1).strip()
            strength = match.group(2)
            unit = match.group(3).lower()
            if name and len(name) >= 1 and strength.count(".") <= 1:
                # Normalise strength
                if "." in strength:
                    val = float(strength)
                    strength = str(val).rstrip("0").rstrip(".")
                return MedicineEntry(
                    medicine_name=name, strength=strength, dosage_unit=unit
                )

        # Name(s) Strength (no unit)
        match = re.match(
            r"^([A-Za-z][A-Za-z\s\-'.]+?)\s+(\d+(?:\.\d+)?)$",
            cleaned,
        )
        if match:
            name = match.group(1).strip()
            strength = match.group(2)
            if name and len(name) >= 2 and strength.count(".") <= 1:
                if "." in strength:
                    val = float(strength)
                    strength = str(val).rstrip("0").rstrip(".")
                return MedicineEntry(
                    medicine_name=name, strength=strength
                )

        return None

    # ── date parsing ────────────────────────────────────────────────

    def _extract_date(self, lines: list[str]) -> str | None:
        """Find and parse a date from the document lines.

        Tries each line with an explicit label first, then falls back
        to scanning all lines.

        Returns ISO 8601 date string (YYYY-MM-DD) or None.
        """
        # First pass: look for labelled date fields
        date_label_patterns = [
            r"(?i)^(?:date|report date|date of report|date of issue|issued on|"
            r"date of collection|collected on|date of birth|dob|"
            r"date of admission|date of discharge)\s*[:.]?\s*(.+)",
        ]

        for line in lines:
            for pattern in date_label_patterns:
                match = re.match(pattern, line)
                if match:
                    parsed = self._parse_date_string(match.group(1).strip())
                    if parsed:
                        return parsed

        # Second pass: scan all lines for date-like patterns
        for line in lines:
            parsed = self._parse_date_string(line)
            if parsed:
                return parsed

        return None

    def _parse_date_string(self, text: str) -> str | None:
        """Parse a date string into ISO format (YYYY-MM-DD).

        Supported formats:
          - DD/MM/YYYY  (tried first; on failure tries MM/DD/YYYY)
          - DD-MM-YYYY  (tried first; on failure tries MM-DD-YYYY)
          - YYYY-MM-DD
          - DD Month YYYY  (e.g. '12 May 2026')
        """
        if not text:
            return None

        # DD/MM/YYYY or DD-MM-YYYY
        match = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", text)
        if match:
            day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
            # Try DD/MM/YYYY
            try:
                return datetime(year, month, day).strftime("%Y-%m-%d")
            except ValueError:
                pass
            # Try MM/DD/YYYY
            try:
                return datetime(year, day, month).strftime("%Y-%m-%d")
            except ValueError:
                pass
            return None

        # YYYY-MM-DD
        match = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", text)
        if match:
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            try:
                return datetime(year, month, day).strftime("%Y-%m-%d")
            except ValueError:
                return None

        # DD Month YYYY (e.g. '12 May 2026', '1st January 2024')
        match = re.search(
            r"(\d{1,2})(?:st|nd|rd|th)?\s+"
            r"(January|February|March|April|May|June|July|"
            r"August|September|October|November|December|"
            r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+"
            r"(\d{4})",
            text,
            re.IGNORECASE,
        )
        if match:
            day = int(match.group(1))
            month_name = match.group(2).lower()
            year = int(match.group(3))
            month = MONTH_MAP.get(month_name)
            if month:
                try:
                    return datetime(year, month, day).strftime("%Y-%m-%d")
                except ValueError:
                    pass
            return None

        return None