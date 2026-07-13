from datetime import time

from pydantic import BaseModel


class DashboardUserSummary(BaseModel):
    id: int
    name: str


class DashboardScheduleItem(BaseModel):
    id: int
    medicine_id: int
    medicine_name: str
    dosage_amount: str | None = None
    dosage_unit: str | None = None
    frequency: str | None = None
    reminder_time: time | None = None


class DashboardInventorySummary(BaseModel):
    total_medicines: int
    expiring_soon: int


class DashboardResponse(BaseModel):
    user: DashboardUserSummary
    greeting: str
    notification_count: int
    today_schedule: list[DashboardScheduleItem]
    inventory_summary: DashboardInventorySummary

