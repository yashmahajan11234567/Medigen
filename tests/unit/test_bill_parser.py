import pytest
from app.core.exceptions import AppException
from app.schemas.bill_parser import BillParseResult, MedicineEntry
from app.services.bill_parser import BillParser


class TestBillParser:
    def setup_method(self):
        self.parser = BillParser()

    # ── single medicine ──────────────────────────────────────────────

    def test_single_medicine_with_qty(self):
        """Parse a single medicine with strength, unit, and quantity."""
        result = self.parser.parse("Paracetamol 500 mg\nQty 10")

        assert isinstance(result, BillParseResult)
        assert len(result.medicines) == 1
        med = result.medicines[0]
        assert med.medicine_name == "Paracetamol"
        assert med.strength == "500"
        assert med.dosage_unit == "mg"
        assert med.quantity == 10.0

    def test_single_medicine_no_qty(self):
        """Parse a single medicine without a quantity line."""
        result = self.parser.parse("Crocin 650")

        assert len(result.medicines) == 1
        med = result.medicines[0]
        assert med.medicine_name == "Crocin"
        assert med.strength == "650"
        assert med.dosage_unit is None
        assert med.quantity is None

    def test_single_medicine_name_only(self):
        """Parse a medicine line with no strength or quantity."""
        result = self.parser.parse("Calpol")

        assert len(result.medicines) == 1
        med = result.medicines[0]
        assert med.medicine_name == "Calpol"
        assert med.strength is None
        assert med.dosage_unit is None
        assert med.quantity is None

    # ── multiple medicines ───────────────────────────────────────────

    def test_multiple_medicines_preserves_order(self):
        """Parse multiple medicines preserving input order."""
        text = (
            "Azithromycin 250 mg\n"
            "Qty 6\n"
            "\n"
            "Ibuprofen 400 mg\n"
            "Qty 10"
        )
        result = self.parser.parse(text)

        assert len(result.medicines) == 2
        assert result.medicines[0].medicine_name == "Azithromycin"
        assert result.medicines[0].strength == "250"
        assert result.medicines[0].quantity == 6.0
        assert result.medicines[1].medicine_name == "Ibuprofen"
        assert result.medicines[1].strength == "400"
        assert result.medicines[1].quantity == 10.0

    def test_multiple_medicines_mixed_qty(self):
        """Parse medicines where some have qty and some don't."""
        text = "Paracetamol 500 mg\nQty 10\n\nCrocin 650"
        result = self.parser.parse(text)

        assert len(result.medicines) == 2
        assert result.medicines[0].medicine_name == "Paracetamol"
        assert result.medicines[0].quantity == 10.0
        assert result.medicines[1].medicine_name == "Crocin"
        assert result.medicines[1].quantity is None

    # ── quantity present / missing ───────────────────────────────────

    def test_quantity_present(self):
        """Verify quantity is extracted correctly."""
        result = self.parser.parse("Amoxicillin 250 mg\nQty 14")
        assert result.medicines[0].quantity == 14.0

    def test_quantity_missing(self):
        """Verify quantity is None when no Qty line follows."""
        result = self.parser.parse("Amoxicillin 250 mg")
        assert result.medicines[0].quantity is None

    # ── malformed input ──────────────────────────────────────────────

    def test_malformed_quantity(self):
        """Reject quantity line with non-numeric value."""
        with pytest.raises(ValueError, match="Invalid quantity format"):
            self.parser.parse("Paracetamol 500 mg\nQty abc")

    def test_malformed_strength(self):
        """Reject strength with multiple decimal points."""
        with pytest.raises(ValueError, match="Invalid strength format"):
            self.parser.parse("Paracetamol 500.5.5 mg\nQty 10")

    def test_strength_zero(self):
        """Handle strength value of zero."""
        result = self.parser.parse("Normal Saline 0 mg\nQty 10")
        assert result.medicines[0].strength == "0"
        assert result.medicines[0].dosage_unit == "mg"

    # ── duplicate medicines ──────────────────────────────────────────

    def test_duplicate_medicines_rejected(self):
        """Reject bill with the same medicine appearing twice."""
        text = "Paracetamol 500 mg\nQty 10\n\nParacetamol 650 mg\nQty 5"
        with pytest.raises(AppException) as exc_info:
            self.parser.parse(text)

        assert exc_info.value.code == "duplicate_medicine"
        assert "Duplicate" in exc_info.value.message

    def test_duplicate_case_insensitive(self):
        """Reject duplicates differing only in case."""
        text = "Paracetamol 500 mg\nQty 10\n\nparacetamol 650 mg"
        with pytest.raises(AppException, match="Duplicate"):
            self.parser.parse(text)

    # ── OCR cleaned text ─────────────────────────────────────────────

    def test_ocr_cleaned_text_standard(self):
        """Parse text as it would come from OCR (similar to normal text)."""
        result = self.parser.parse("Cetirizine 10 mg\nQty 30")
        assert result.medicines[0].medicine_name == "Cetirizine"
        assert result.medicines[0].strength == "10"
        assert result.medicines[0].dosage_unit == "mg"
        assert result.medicines[0].quantity == 30.0

    def test_ocr_noisy_quantity_format(self):
        """Handle OCR variants of quantity markers."""
        result = self.parser.parse("Metformin 500 mg\nQty: 60")
        assert result.medicines[0].quantity == 60.0

        result = self.parser.parse("Metformin 500 mg\nQuantity 60")
        assert result.medicines[0].quantity == 60.0

        result = self.parser.parse("Metformin 500 mg\nqty. 60")
        assert result.medicines[0].quantity == 60.0

    # ── empty input ──────────────────────────────────────────────────

    def test_empty_input(self):
        """Reject empty text."""
        with pytest.raises(ValueError, match="Empty or whitespace-only input"):
            self.parser.parse("")

    def test_whitespace_only_input(self):
        """Reject whitespace-only text."""
        with pytest.raises(ValueError, match="Empty or whitespace-only input"):
            self.parser.parse("   \n  \t  ")

    # ── unusual spacing ──────────────────────────────────────────────

    def test_unusual_spacing(self):
        """Handle extra whitespace between tokens."""
        result = self.parser.parse("  Paracetamol   500   mg  \n  Qty   10  ")
        assert result.medicines[0].medicine_name == "Paracetamol"
        assert result.medicines[0].strength == "500"
        assert result.medicines[0].dosage_unit == "mg"
        assert result.medicines[0].quantity == 10.0

    # ── edge cases ──────────────────────────────────────────────────

    def test_decimal_strength(self):
        """Parse decimal strength values."""
        result = self.parser.parse("Warfarin 2.5 mg\nQty 30")
        assert result.medicines[0].strength == "2.5"
        assert result.medicines[0].dosage_unit == "mg"

    def test_strength_trailing_zero_removed(self):
        """Normalise 10.0 strength to 10."""
        result = self.parser.parse("Cetirizine 10.0 mg\nQty 30")
        assert result.medicines[0].strength == "10"

    def test_quantity_with_decimal(self):
        """Parse decimal quantity values."""
        result = self.parser.parse("Amoxicillin 250 mg\nQty 10.5")
        assert result.medicines[0].quantity == 10.5

    def test_quantity_line_first_is_error(self):
        """Reject text that starts with a quantity line."""
        with pytest.raises(
            ValueError, match="Unexpected quantity line without preceding medicine"
        ):
            self.parser.parse("Qty 10\nParacetamol 500 mg")

    def test_raw_text_preserved_in_result(self):
        """Verify raw_text field contains the original input."""
        text = "Paracetamol 500 mg\nQty 10"
        result = self.parser.parse(text)
        assert result.raw_text == text.strip()

    def test_multi_word_medicine_name(self):
        """Handle medicine names with multiple words."""
        result = self.parser.parse("Calcium Carbonate 500 mg\nQty 60")
        assert result.medicines[0].medicine_name == "Calcium Carbonate"
        assert result.medicines[0].strength == "500"
        assert result.medicines[0].dosage_unit == "mg"

    def test_no_strength_unit_with_qty(self):
        """Handle medicine with no strength but with quantity."""
        result = self.parser.parse("Glucose\nQty 5")
        assert result.medicines[0].medicine_name == "Glucose"
        assert result.medicines[0].strength is None
        assert result.medicines[0].dosage_unit is None
        assert result.medicines[0].quantity == 5.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])