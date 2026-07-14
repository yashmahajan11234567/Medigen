from datetime import date, timedelta

import pytest

from app.core.enums import FoodTiming, InventoryStatus, MedicineType
from app.core.exceptions import AppException
from app.repositories.schedule_repository import ScheduleRepository
from app.schemas.inventory import InventoryUpdateRequest
from app.schemas.medical_records import MedicalRecordCreateRequest
from app.schemas.schedule import ScheduleCompleteRequest, ScheduleCreateRequest, ScheduleUpdateRequest
from app.services.dashboard_service import DashboardService
from app.services.generic_finder_service import GenericFinderService
from app.services.inventory_service import InventoryService
from app.services.medical_record_service import MedicalRecordService
from app.services.scheduler_service import SchedulerService
from tests.support import create_inventory_item, create_medicine, create_user


def test_dashboard_reflects_live_scheduler_and_inventory_state(db_session):
    user = create_user(db_session, email="integration-dashboard@example.com")
    medicine = create_medicine(db_session, name="Dashboard Sync Med", dosage_form=MedicineType.TABLET)
    create_inventory_item(
        db_session,
        user_id=user.id,
        medicine_id=medicine.id,
        status=InventoryStatus.AVAILABLE,
        quantity=8,
        expiry_date=date.today() + timedelta(days=5),
    )
    SchedulerService(db_session).create_schedule(
        user_id=user.id,
        payload=ScheduleCreateRequest(
            medicine_id=medicine.id,
            dosage_pattern="1-0-0",
            food_timing=FoodTiming.AFTER_FOOD,
            start_date=date.today(),
            duration_days=2,
            quantity=6,
            quantity_unit="tablets",
        ),
    )

    dashboard = DashboardService(db_session).get_dashboard(user.id)

    assert len(dashboard.today_schedule) == 1
    assert dashboard.today_schedule[0].medicine_name == "Dashboard Sync Med"
    assert dashboard.inventory_summary.total_medicines == 2
    assert dashboard.inventory_summary.expiring_soon == 1


def test_generic_finder_to_inventory_is_visible_in_dashboard_and_prevents_duplicates(db_session):
    user = create_user(db_session, email="integration-generic@example.com")
    generic_medicine = create_medicine(
        db_session,
        name="Paracetamol Generic",
        generic_name="Paracetamol",
        brand_name=None,
        dosage_form=MedicineType.TABLET,
    )
    generic_finder = GenericFinderService(db_session)

    added = generic_finder.add_to_inventory(user_id=user.id, medicine_id=generic_medicine.id, quantity=3, quantity_unit="tablets")
    dashboard = DashboardService(db_session).get_dashboard(user.id)

    assert added.medicine_id == generic_medicine.id
    assert dashboard.inventory_summary.total_medicines == 1

    with pytest.raises(AppException) as exc_info:
        generic_finder.add_to_inventory(user_id=user.id, medicine_id=generic_medicine.id, quantity=3, quantity_unit="tablets")

    assert exc_info.value.code == "duplicate_medicine"
    assert DashboardService(db_session).get_dashboard(user.id).inventory_summary.total_medicines == 1


def test_medical_record_links_remain_valid_after_schedule_and_inventory_updates(db_session):
    user = create_user(db_session, email="integration-record-links@example.com")
    medicine = create_medicine(db_session, name="Linked Med", dosage_form=MedicineType.TABLET)
    scheduler_service = SchedulerService(db_session)
    inventory_service = InventoryService(db_session)
    medical_record_service = MedicalRecordService(db_session)

    created_schedule = scheduler_service.create_schedule(
        user_id=user.id,
        payload=ScheduleCreateRequest(
            medicine_id=medicine.id,
            dosage_pattern="1-0-1",
            food_timing=FoodTiming.AFTER_FOOD,
            start_date=date.today(),
            duration_days=3,
            quantity=10,
            quantity_unit="tablets",
        ),
    )
    created_inventory = inventory_service.list_inventory(user_id=user.id).items[0]

    created_record = medical_record_service.create_record(
        user_id=user.id,
        payload=MedicalRecordCreateRequest(
            title="Integrated Record",
            folder_name="Phase 7",
            hospital_name="City Hospital",
            doctor_name="Dr. Patel",
            visit_date=date.today(),
            linked_schedule_ids=[created_schedule.id],
            linked_inventory_item_ids=[created_inventory.id],
            linked_medicine_ids=[medicine.id],
            documents=[
                {
                    "document_type": "prescription",
                    "file_name": "phase7.pdf",
                    "file_type": "application/pdf",
                    "file_size": 1024,
                    "storage_path": "/records/phase7.pdf",
                }
            ],
        ),
    )

    scheduler_service.update_schedule(
        user_id=user.id,
        schedule_id=created_schedule.id,
        payload=ScheduleUpdateRequest(
            dosage_pattern="0-1-0",
            food_timing=FoodTiming.BEFORE_FOOD,
            duration_days=3,
            quantity=8,
            quantity_unit="tablets",
        ),
    )
    inventory_service.update_inventory_item(
        user_id=user.id,
        inventory_id=created_inventory.id,
        payload=InventoryUpdateRequest(
            type=MedicineType.TABLET,
            quantity=7,
            quantity_unit="tablets",
            expiry_date=date.today() + timedelta(days=40),
        ),
    )

    refreshed_record = medical_record_service.get_record(user_id=user.id, record_id=created_record.id)

    assert refreshed_record.linked_schedule_ids == [created_schedule.id]
    assert refreshed_record.linked_inventory_item_ids == [created_inventory.id]
    assert refreshed_record.linked_medicine_ids == [medicine.id]


def test_scheduler_completion_consumes_inventory(db_session):
    user = create_user(db_session, email="integration-consume@example.com")
    medicine = create_medicine(db_session, name="Consume Med", dosage_form=MedicineType.TABLET)
    scheduler_service = SchedulerService(db_session)

    created = scheduler_service.create_schedule(
        user_id=user.id,
        payload=ScheduleCreateRequest(
            medicine_id=medicine.id,
            dosage_pattern="2-0-0",
            food_timing=FoodTiming.AFTER_FOOD,
            start_date=date.today(),
            duration_days=1,
            quantity=4,
            quantity_unit="tablets",
        ),
    )

    completed = scheduler_service.complete_reminder(
        user_id=user.id,
        payload=ScheduleCompleteRequest(reminder_id=created.reminders[0].id),
    )
    inventory_item = InventoryService(db_session).list_inventory(user_id=user.id).items[0]

    assert completed.completed_at is not None
    assert inventory_item.quantity == 2
    assert inventory_item.status in {InventoryStatus.LOW_STOCK, InventoryStatus.AVAILABLE}


def test_scheduler_completion_rolls_back_when_inventory_sync_fails(db_session, monkeypatch):
    user = create_user(db_session, email="integration-rollback@example.com")
    medicine = create_medicine(db_session, name="Rollback Med", dosage_form=MedicineType.TABLET)
    scheduler_service = SchedulerService(db_session)

    created = scheduler_service.create_schedule(
        user_id=user.id,
        payload=ScheduleCreateRequest(
            medicine_id=medicine.id,
            dosage_pattern="1-0-0",
            food_timing=FoodTiming.AFTER_FOOD,
            start_date=date.today(),
            duration_days=1,
            quantity=4,
            quantity_unit="tablets",
        ),
    )

    def failing_consume(**kwargs):
        raise AppException("Inventory sync failed.", 500, "inventory_sync_failed")

    monkeypatch.setattr(
        scheduler_service.inventory_integration_service,
        "consume_scheduler_medicine",
        failing_consume,
    )

    with pytest.raises(AppException) as exc_info:
        scheduler_service.complete_reminder(
            user_id=user.id,
            payload=ScheduleCompleteRequest(reminder_id=created.reminders[0].id),
        )

    reminder = ScheduleRepository(db_session).get_reminder_by_id(
        user_id=user.id,
        reminder_id=created.reminders[0].id,
    )
    inventory_item = InventoryService(db_session).list_inventory(user_id=user.id).items[0]

    assert exc_info.value.code == "inventory_integration_failure"
    assert reminder.completed_at is None
    assert inventory_item.quantity == 4


def test_dashboard_contract_remains_unchanged_after_medical_record_creation(db_session):
    user = create_user(db_session, email="integration-dashboard-record@example.com")
    medicine = create_medicine(db_session, name="Record Dashboard Med", dosage_form=MedicineType.TABLET)
    MedicalRecordService(db_session).create_record(
        user_id=user.id,
        payload=MedicalRecordCreateRequest(
            title="Dashboard Stability",
            folder_name="Records",
            linked_medicine_ids=[medicine.id],
        ),
    )

    dashboard = DashboardService(db_session).get_dashboard(user.id)

    assert set(dashboard.model_dump().keys()) == {
        "user",
        "greeting",
        "notification_count",
        "today_schedule",
        "inventory_summary",
    }
