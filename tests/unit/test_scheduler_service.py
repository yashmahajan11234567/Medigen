from datetime import date, timedelta

import pytest

from app.core.enums import FoodTiming, MedicineType, ReminderPeriod
from app.core.exceptions import AppException
from app.schemas.schedule import (
    BillMedicineInput,
    ReminderTimesInput,
    ScheduleCompleteRequest,
    ScheduleCreateRequest,
)
from app.services.scheduler_service import SchedulerService
from tests.support import create_inventory_item, create_medicine, create_user


def test_scheduler_service_creates_schedule_and_generates_reminders(db_session):
    user = create_user(db_session, email="scheduler-service@example.com")
    medicine = create_medicine(db_session, name="Schedule Tablet", dosage_form=MedicineType.TABLET)
    service = SchedulerService(db_session)

    created = service.create_schedule(
        user_id=user.id,
        payload=ScheduleCreateRequest(
            medicine_id=medicine.id,
            dosage_pattern="1-0-1",
            food_timing=FoodTiming.AFTER_FOOD,
            start_date=date.today(),
            duration_days=2,
            quantity=10,
            quantity_unit="tablets",
        ),
    )

    assert created.dosage_pattern == "1-0-1"
    assert len(created.reminders) == 4
    assert created.reminders[0].period == ReminderPeriod.MORNING


def test_scheduler_service_rejects_duplicate_active_schedule(db_session):
    user = create_user(db_session, email="scheduler-duplicate@example.com")
    medicine = create_medicine(db_session, name="Schedule Tablet", dosage_form=MedicineType.TABLET)
    service = SchedulerService(db_session)
    service.create_schedule(
        user_id=user.id,
        payload=ScheduleCreateRequest(
            medicine_id=medicine.id,
            dosage_pattern="1-0-0",
            food_timing=FoodTiming.AFTER_FOOD,
            start_date=date.today(),
            duration_days=3,
            quantity=6,
            quantity_unit="tablets",
        ),
    )

    with pytest.raises(AppException) as exc_info:
        service.create_schedule(
            user_id=user.id,
            payload=ScheduleCreateRequest(
                medicine_id=medicine.id,
                dosage_pattern="0-1-0",
                food_timing=FoodTiming.BEFORE_FOOD,
                start_date=date.today() + timedelta(days=1),
                duration_days=3,
                quantity=6,
                quantity_unit="tablets",
            ),
        )

    assert exc_info.value.code == "duplicate_active_schedule"


def test_scheduler_service_returns_todays_schedule(db_session):
    user = create_user(db_session, email="scheduler-today@example.com")
    medicine = create_medicine(db_session, name="Today Med", dosage_form=MedicineType.TABLET)
    service = SchedulerService(db_session)
    service.create_schedule(
        user_id=user.id,
        payload=ScheduleCreateRequest(
            medicine_id=medicine.id,
            dosage_pattern="0-1-0",
            food_timing=FoodTiming.AFTER_FOOD,
            start_date=date.today(),
            duration_days=1,
            quantity=5,
            quantity_unit="tablets",
            reminder_times=ReminderTimesInput(afternoon=None),
        ),
    )

    today_schedule = service.get_todays_schedule(user_id=user.id)

    assert len(today_schedule.items) == 1
    assert len(today_schedule.items[0].reminders) == 1


def test_scheduler_service_creates_schedule_from_bill_and_integrates_inventory(db_session):
    user = create_user(db_session, email="scheduler-bill@example.com")
    create_medicine(
        db_session,
        name="Crocin 500",
        brand_name="Crocin 500",
        generic_name="Paracetamol",
        dosage_form=MedicineType.TABLET,
    )
    service = SchedulerService(db_session)

    created = service.create_schedule_from_bill(
        user_id=user.id,
        payload=BillMedicineInput(
            medicine_name="Crocin 500",
            quantity=8,
            purchase_date=date.today(),
            expiry_date=date.today() + timedelta(days=90),
            pharmacy_name="Apollo",
            dosage_pattern="1-0-1",
            food_timing=FoodTiming.AFTER_FOOD,
            start_date=date.today(),
            duration_days=5,
        ),
    )

    assert created.source.value == "pharmacy_bill"


def test_scheduler_service_completes_reminder(db_session):
    user = create_user(db_session, email="scheduler-complete@example.com")
    medicine = create_medicine(db_session, name="Complete Med", dosage_form=MedicineType.TABLET)
    service = SchedulerService(db_session)
    created = service.create_schedule(
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

    completed = service.complete_reminder(
        user_id=user.id,
        payload=ScheduleCompleteRequest(reminder_id=created.reminders[0].id),
    )

    assert completed.completed_at is not None


def test_scheduler_service_rejects_expired_medicine_bill(db_session):
    user = create_user(db_session, email="scheduler-expired@example.com")
    create_medicine(
        db_session,
        name="Expired Med",
        brand_name="Expired Med",
        generic_name="Paracetamol",
        dosage_form=MedicineType.TABLET,
    )
    service = SchedulerService(db_session)

    with pytest.raises(AppException) as exc_info:
        service.create_schedule_from_bill(
            user_id=user.id,
            payload=BillMedicineInput(
                medicine_name="Expired Med",
                quantity=5,
                purchase_date=date.today() - timedelta(days=100),
                expiry_date=date.today() - timedelta(days=1),
                pharmacy_name="Apollo",
                dosage_pattern="1-0-0",
                food_timing=FoodTiming.AFTER_FOOD,
                start_date=date.today(),
                duration_days=2,
            ),
        )

    assert exc_info.value.code == "expired_medicine"

