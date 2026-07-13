from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.enums import MedicalRecordDocumentType


class MedicalRecordDocumentCreate(BaseModel):
    document_type: MedicalRecordDocumentType
    file_name: str = Field(min_length=1, max_length=255)
    file_type: str = Field(min_length=1, max_length=100)
    file_size: int = Field(gt=0)
    storage_path: str = Field(min_length=1, max_length=500)
    upload_date: datetime | None = None
    doctor_name: str | None = Field(default=None, max_length=255)
    hospital_or_clinic: str | None = Field(default=None, max_length=255)
    doctor_specialty: str | None = Field(default=None, max_length=255)
    consultation_date: date | None = None
    follow_up_date: date | None = None
    diagnosis: str | None = Field(default=None, max_length=255)
    notes: str | None = None

    @field_validator("file_name", "file_type", "storage_path")
    @classmethod
    def validate_non_blank_strings(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field cannot be blank.")
        return normalized

    @model_validator(mode="after")
    def validate_dates(self):
        if self.follow_up_date and self.consultation_date and self.follow_up_date < self.consultation_date:
            raise ValueError("Follow-up date cannot be earlier than consultation date.")
        return self


class MedicalRecordCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    folder_name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    hospital_name: str | None = Field(default=None, max_length=255)
    doctor_name: str | None = Field(default=None, max_length=255)
    visit_date: date | None = None
    diagnosis: str | None = Field(default=None, max_length=255)
    treatment_name: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    documents: list[MedicalRecordDocumentCreate] = Field(default_factory=list)
    linked_schedule_ids: list[int] = Field(default_factory=list)
    linked_inventory_item_ids: list[int] = Field(default_factory=list)
    linked_medicine_ids: list[int] = Field(default_factory=list)
    linked_generic_search_ids: list[str] = Field(default_factory=list)

    @field_validator("title", "folder_name")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field cannot be blank.")
        return normalized


class MedicalRecordUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    folder_name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    hospital_name: str | None = Field(default=None, max_length=255)
    doctor_name: str | None = Field(default=None, max_length=255)
    visit_date: date | None = None
    diagnosis: str | None = Field(default=None, max_length=255)
    treatment_name: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    documents: list[MedicalRecordDocumentCreate] | None = None
    linked_generic_search_ids: list[str] | None = None

    @field_validator("title", "folder_name")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field cannot be blank.")
        return normalized


class MedicalRecordLinkRequest(BaseModel):
    record_id: int = Field(gt=0)
    schedule_ids: list[int] = Field(default_factory=list)
    inventory_item_ids: list[int] = Field(default_factory=list)
    medicine_ids: list[int] = Field(default_factory=list)


class MedicalRecordDocumentResponse(BaseModel):
    id: int
    document_type: MedicalRecordDocumentType
    file_name: str
    file_type: str
    file_size: int
    storage_path: str
    upload_date: datetime
    doctor_name: str | None = None
    hospital_or_clinic: str | None = None
    doctor_specialty: str | None = None
    consultation_date: date | None = None
    follow_up_date: date | None = None
    diagnosis: str | None = None
    notes: str | None = None


class MedicalRecordResponse(BaseModel):
    id: int
    title: str
    folder_name: str
    description: str | None = None
    hospital_name: str | None = None
    doctor_name: str | None = None
    visit_date: date | None = None
    diagnosis: str | None = None
    treatment_name: str | None = None
    notes: str | None = None
    documents: list[MedicalRecordDocumentResponse]
    linked_schedule_ids: list[int]
    linked_inventory_item_ids: list[int]
    linked_medicine_ids: list[int]
    linked_generic_search_ids: list[str]
    created_at: datetime
    updated_at: datetime


class MedicalRecordListResponse(BaseModel):
    items: list[MedicalRecordResponse]


class MedicalRecordDeleteResponse(BaseModel):
    message: str
