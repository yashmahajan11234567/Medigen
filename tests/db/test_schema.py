from app.db.base import Base
from app.models import load_all_models


load_all_models()


def test_expected_tables_exist():
    expected_tables = {
        "users",
        "medicines",
        "inventory",
        "schedules",
        "schedule_reminders",
        "medical_records",
        "medical_record_documents",
        "medical_record_schedules",
        "medical_record_inventory_items",
        "medical_record_medicines",
        "notifications",
    }

    assert expected_tables.issubset(Base.metadata.tables.keys())
