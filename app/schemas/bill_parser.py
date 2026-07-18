from pydantic import BaseModel, Field, field_validator


class MedicineEntry(BaseModel):
    """A single medicine parsed from a pharmacy bill."""

    medicine_name: str = Field(min_length=1, max_length=255)
    strength: str | None = None
    dosage_unit: str | None = None
    quantity: float | None = None

    @field_validator("medicine_name")
    @classmethod
    def strip_medicine_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Medicine name must not be blank.")
        return normalized

    @field_validator("dosage_unit")
    @classmethod
    def strip_dosage_unit(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class BillParseResult(BaseModel):
    """Structured result from parsing a pharmacy bill."""

    medicines: list[MedicineEntry] = Field(min_length=1)
    raw_text: str