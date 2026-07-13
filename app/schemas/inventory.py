from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.enums import InventoryStatus, MedicineType


class InventoryItemBase(BaseModel):
    medicine_id: int | None = Field(default=None, gt=0)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    generic_name: str | None = Field(default=None, max_length=255)
    brand_name: str | None = Field(default=None, max_length=255)
    type: MedicineType
    quantity: float | None = None
    quantity_unit: str | None = Field(default=None, max_length=50)
    expiry_date: date | None = None
    purchase_date: date | None = None
    image_path: str | None = Field(default=None, max_length=500)
    notes: str | None = None

    @field_validator("name", "generic_name", "brand_name", "quantity_unit", "image_path", "notes", mode="before")
    @classmethod
    def strip_optional_strings(cls, value):
        if value is None:
            return value
        normalized = str(value).strip()
        return normalized or None


class InventoryCreateRequest(InventoryItemBase):
    @field_validator("name")
    @classmethod
    def ensure_name_or_medicine_id(cls, value):
        return value


class InventoryUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    generic_name: str | None = Field(default=None, max_length=255)
    brand_name: str | None = Field(default=None, max_length=255)
    type: MedicineType | None = None
    quantity: float | None = None
    quantity_unit: str | None = Field(default=None, max_length=50)
    expiry_date: date | None = None
    purchase_date: date | None = None
    image_path: str | None = Field(default=None, max_length=500)
    notes: str | None = None

    @field_validator("name", "generic_name", "brand_name", "quantity_unit", "image_path", "notes", mode="before")
    @classmethod
    def strip_optional_strings(cls, value):
        if value is None:
            return value
        normalized = str(value).strip()
        return normalized or None


class InventoryResponseItem(BaseModel):
    id: int
    medicine_id: int
    name: str
    generic_name: str | None = None
    brand_name: str | None = None
    type: MedicineType
    quantity: float | None = None
    quantity_unit: str | None = None
    status: InventoryStatus
    expiry_date: date | None = None
    purchase_date: date | None = None
    image_path: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InventoryListResponse(BaseModel):
    items: list[InventoryResponseItem]


class InventorySummaryResponse(BaseModel):
    total_medicines: int
    available_medicines: int
    finished_medicines: int
    expiring_soon: int
    expired: int


class InventoryDeleteResponse(BaseModel):
    message: str
