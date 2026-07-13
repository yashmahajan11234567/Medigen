from datetime import date, datetime, time

from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.enums import FoodTiming, ReminderPeriod, ScheduleSource, ScheduleStatus


class ReminderTimesInput(BaseModel):
    morning: time | None = None
    afternoon: time | None = None
    night: time | None = None


class ScheduleBaseRequest(BaseModel):
    medicine_id: int = Field(gt=0)
    dosage_pattern: str = Field(min_length=5, max_length=20)
    food_timing: FoodTiming
    start_date: date
    end_date: date | None = None
    duration_days: int | None = Field(default=None, gt=0)
    reminder_times: ReminderTimesInput | None = None
    notes: str | None = None
    quantity: float | None = Field(default=None, ge=0)
    quantity_unit: str | None = Field(default=None, max_length=50)
    purchase_date: date | None = None
    expiry_date: date | None = None
    pharmacy_name: str | None = Field(default=None, max_length=255)

    @field_validator("dosage_pattern")
    @classmethod
    def validate_dosage_pattern(cls, value: str) -> str:
        parts = value.strip().split("-")
        if len(parts) != 3 or any((not part.isdigit()) for part in parts):
            raise ValueError("Dosage pattern must use the Morning-Afternoon-Night format, such as 1-0-1.")
        if all(int(part) == 0 for part in parts):
            raise ValueError("Dosage pattern must schedule at least one reminder.")
        return value.strip()

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("End date cannot be earlier than start date.")
        if self.purchase_date and self.expiry_date and self.expiry_date < self.purchase_date:
            raise ValueError("Expiry date cannot be earlier than purchase date.")
        return self


class ScheduleCreateRequest(ScheduleBaseRequest):
    source: ScheduleSource = ScheduleSource.MANUAL


class ScheduleUpdateRequest(BaseModel):
    dosage_pattern: str | None = Field(default=None, min_length=5, max_length=20)
    food_timing: FoodTiming | None = None
    start_date: date | None = None
    end_date: date | None = None
    duration_days: int | None = Field(default=None, gt=0)
    reminder_times: ReminderTimesInput | None = None
    notes: str | None = None
    quantity: float | None = Field(default=None, ge=0)
    quantity_unit: str | None = Field(default=None, max_length=50)
    purchase_date: date | None = None
    expiry_date: date | None = None
    pharmacy_name: str | None = Field(default=None, max_length=255)
    status: ScheduleStatus | None = None


class BillMedicineInput(BaseModel):
    medicine_name: str = Field(min_length=1, max_length=255)
    quantity: float | None = Field(default=None, ge=0)
    purchase_date: date | None = None
    expiry_date: date | None = None
    pharmacy_name: str | None = Field(default=None, max_length=255)
    dosage_pattern: str = Field(min_length=5, max_length=20)
    food_timing: FoodTiming
    start_date: date
    end_date: date | None = None
    duration_days: int | None = Field(default=None, gt=0)
    reminder_times: ReminderTimesInput | None = None
    notes: str | None = None

    @field_validator("dosage_pattern")
    @classmethod
    def validate_dosage_pattern(cls, value: str) -> str:
        parts = value.strip().split("-")
        if len(parts) != 3 or any((not part.isdigit()) for part in parts):
            raise ValueError("Dosage pattern must use the Morning-Afternoon-Night format, such as 1-0-1.")
        if all(int(part) == 0 for part in parts):
            raise ValueError("Dosage pattern must schedule at least one reminder.")
        return value.strip()


class ScheduleCompleteRequest(BaseModel):
    reminder_id: int = Field(gt=0)


class ScheduleReminderResponse(BaseModel):
    id: int
    reminder_date: date
    reminder_time: time
    period: ReminderPeriod
    completed_at: datetime | None = None


class ScheduleResponse(BaseModel):
    id: int
    medicine_id: int
    medicine_name: str
    dosage_pattern: str
    food_timing: FoodTiming
    start_date: date
    end_date: date
    duration_days: int | None = None
    quantity: float | None = None
    quantity_unit: str | None = None
    purchase_date: date | None = None
    expiry_date: date | None = None
    pharmacy_name: str | None = None
    notes: str | None = None
    status: ScheduleStatus
    source: ScheduleSource
    reminder_time: time | None = None
    reminders: list[ScheduleReminderResponse]


class ScheduleListResponse(BaseModel):
    items: list[ScheduleResponse]


class ScheduleDeleteResponse(BaseModel):
    message: str
