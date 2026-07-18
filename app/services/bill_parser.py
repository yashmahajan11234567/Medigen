import re

from app.core.exceptions import AppException
from app.schemas.bill_parser import BillParseResult, MedicineEntry


class BillParser:
    """Parse cleaned OCR text from pharmacy bills into structured medicine entries.

    Supported input formats:

        Paracetamol 500 mg
        Qty 10

        Crocin 650

        Azithromycin 250 mg
        Qty 6

        Ibuprofen 400 mg
        Qty 10
    """

    def parse(self, raw_text: str) -> BillParseResult:
        """Transform cleaned OCR bill text into a BillParseResult.

        Args:
            raw_text: Cleaned text from OCRService.

        Returns:
            BillParseResult with ordered list of MedicineEntry instances.

        Raises:
            ValueError: For empty input, malformed strengths, or malformed quantities.
            AppException: For duplicate medicine entries.
        """
        if not raw_text or not raw_text.strip():
            raise ValueError("Empty or whitespace-only input")

        text = raw_text.strip()
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        medicines: list[MedicineEntry] = []
        seen_names: set[str] = set()

        i = 0
        while i < len(lines):
            line = lines[i]

            # A quantity line at the start is invalid
            if self._is_quantity_line(line):
                raise ValueError(
                    f"Unexpected quantity line without preceding medicine: '{line}'"
                )

            # Parse the medicine line
            medicine = self._parse_medicine_line(line)

            # Check for duplicate (case-insensitive)
            name_key = medicine.medicine_name.lower().strip()
            if name_key in seen_names:
                raise AppException(
                    message=f"Duplicate medicine entry: '{medicine.medicine_name}'",
                    status_code=422,
                    code="duplicate_medicine",
                )
            seen_names.add(name_key)

            # Check if the next line is a quantity line
            if i + 1 < len(lines) and self._is_quantity_line(lines[i + 1]):
                qty_line = lines[i + 1]
                medicine.quantity = self._parse_quantity(qty_line)
                i += 2
            else:
                i += 1

            medicines.append(medicine)

        return BillParseResult(medicines=medicines, raw_text=text)

    def _is_quantity_line(self, line: str) -> bool:
        """Check if a line is a quantity indicator (e.g. 'Qty 10')."""
        return bool(re.match(r"(?i)^(?:qty|quantity)", line.strip()))

    def _parse_quantity(self, line: str) -> float:
        """Extract the numeric quantity from a quantity line.

        Raises:
            ValueError: If no valid number is found.
        """
        match = re.search(r"(\d+(?:\.\d+)?)", line)
        if not match:
            raise ValueError(f"Invalid quantity format: '{line}'")
        try:
            return float(match.group(1))
        except ValueError:
            raise ValueError(f"Invalid quantity format: '{line}'")

    def _parse_medicine_line(self, line: str) -> MedicineEntry:
        """Parse a single medicine line into a MedicineEntry.

        Handles formats:
          - 'Paracetamol 500 mg'         → name, strength='500',   unit='mg'
          - 'Crocin 650'                 → name, strength='650',   unit=None
          - 'Calcium Carbonate 500 mg'   → name, strength='500',   unit='mg'
          - 'Paracetamol 500mg'          → name, strength='500',   unit='mg'
          - 'Paracetamol'                → name, strength=None,     unit=None

        Uses word-boundary detection: the FIRST word that starts with a
        digit is treated as the strength token.  Everything before it is
        the medicine name.  This correctly handles multi-word names
        (e.g. 'Vitamin B12 1000 mcg' → name='Vitamin B12',
        strength='1000', unit='mcg').
        """
        line = line.strip()
        if not line:
            raise ValueError("Empty medicine line")

        if self._is_quantity_line(line):
            raise ValueError(
                f"Expected medicine name, got quantity line: '{line}'"
            )

        words = line.split()

        # Find the first word that starts with a digit (the strength token)
        strength_idx = None
        for i, word in enumerate(words):
            if word and word[0].isdigit():
                strength_idx = i
                break

        if strength_idx is not None:
            # Everything before the strength word is the medicine name
            name = " ".join(words[:strength_idx]).strip()
            strength_token = words[strength_idx]

            # Extract all consecutive digits and decimal points from the
            # start of the strength token (handles '500mg', '500.5', etc.)
            pos = 0
            chars: list[str] = []
            while pos < len(strength_token) and (
                strength_token[pos].isdigit() or strength_token[pos] == "."
            ):
                chars.append(strength_token[pos])
                pos += 1
            strength_str = "".join(chars)

            # Validate strength
            if not strength_str:
                raise ValueError(f"Invalid strength format: '{strength_token}'")
            if strength_str.count(".") > 1:
                raise ValueError(f"Invalid strength format: '{strength_str}'")
            try:
                float(strength_str)
            except ValueError:
                raise ValueError(f"Invalid strength format: '{strength_str}'")

            # Normalise strength (strip trailing zeros after decimal)
            if "." in strength_str:
                val = float(strength_str)
                strength = str(val).rstrip("0").rstrip(".")
            else:
                strength = strength_str

            # Determine unit
            remaining_in_token = strength_token[pos:]  # e.g. 'mg' from '500mg'
            if remaining_in_token:
                dosage_unit = remaining_in_token.lower()
            elif strength_idx + 1 < len(words):
                dosage_unit = words[strength_idx + 1].lower()
            else:
                dosage_unit = None

            if not name:
                raise ValueError(
                    f"Medicine name cannot be empty in line: '{line}'"
                )

            return MedicineEntry(
                medicine_name=name,
                strength=strength,
                dosage_unit=dosage_unit,
                quantity=None,
            )
        else:
            # No numeric strength — entire line is the medicine name
            return MedicineEntry(
                medicine_name=line,
                strength=None,
                dosage_unit=None,
                quantity=None,
            )