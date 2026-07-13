from enum import StrEnum


class MedicineType(StrEnum):
    TABLET = "tablet"
    CAPSULE = "capsule"
    SYRUP = "syrup"
    CREAM = "cream"
    INJECTION = "injection"
    OINTMENT = "ointment"
    DROPS = "drops"
    INHALER = "inhaler"
    OTHER = "other"


class InventoryStatus(StrEnum):
    AVAILABLE = "available"
    LOW_STOCK = "low_stock"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"
    OUT_OF_STOCK = "out_of_stock"


class ScheduleStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ScheduleSource(StrEnum):
    MANUAL = "manual"
    PHARMACY_BILL = "pharmacy_bill"
    GENERIC_FINDER = "generic_finder"


class FoodTiming(StrEnum):
    BEFORE_FOOD = "before_food"
    AFTER_FOOD = "after_food"


class ReminderPeriod(StrEnum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    NIGHT = "night"


class NotificationType(StrEnum):
    REMINDER = "reminder"
    EXPIRY = "expiry"
    SYSTEM = "system"


class NotificationStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    READ = "read"
    ARCHIVED = "archived"


class MedicalRecordDocumentType(StrEnum):
    PRESCRIPTION = "prescription"
    PHARMACY_BILL = "pharmacy_bill"
    OTHER_DOCUMENT = "other_document"
