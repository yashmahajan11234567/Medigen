from app.models.inventory import InventoryItem
from app.models.medical_record import (
    MedicalRecord,
    MedicalRecordDocument,
    medical_record_inventory_items,
    medical_record_medicines,
    medical_record_schedules,
)
from app.models.medicine import Medicine
from app.models.notification import Notification
from app.models.schedule import Schedule
from app.models.schedule_reminder import ScheduleReminder
from app.models.user import User


__all__ = [
    "InventoryItem",
    "MedicalRecord",
    "MedicalRecordDocument",
    "medical_record_inventory_items",
    "medical_record_medicines",
    "medical_record_schedules",
    "Medicine",
    "Notification",
    "Schedule",
    "ScheduleReminder",
    "User",
    "load_all_models",
]


def load_all_models() -> None:
    """Import all model modules so SQLAlchemy metadata is populated."""
