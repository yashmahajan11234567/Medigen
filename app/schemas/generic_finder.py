from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.enums import MedicineType


class CanonicalComposition(BaseModel):
    ingredient: str = Field(min_length=1, max_length=255)
    strength: str = Field(min_length=1, max_length=100)
    unit: str = Field(min_length=1, max_length=50)
    dosage_form: MedicineType
    route: str = Field(min_length=1, max_length=50)

    @field_validator("ingredient", "strength", "unit", "route")
    @classmethod
    def strip_required_strings(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Field must not be blank.")
        return normalized


class GenericMedicineSummary(BaseModel):
    id: int
    name: str
    generic_name: str | None = None
    brand_name: str | None = None
    composition: CanonicalComposition

    model_config = ConfigDict(from_attributes=True)


class GenericFinderSearchResponse(BaseModel):
    source_medicine: GenericMedicineSummary | None = None
    normalized_composition: CanonicalComposition
    matches: list[GenericMedicineSummary]
    message: str


class GenericMedicineDetailResponse(BaseModel):
    medicine: GenericMedicineSummary
    is_generic: bool


class AddToInventoryRequest(BaseModel):
    medicine_id: int = Field(gt=0)
    quantity: float | None = Field(default=None, ge=0)
    quantity_unit: str | None = Field(default=None, max_length=50)
    expiry_date: date | None = None


class AddToInventoryResponse(BaseModel):
    message: str
    medicine_id: int
