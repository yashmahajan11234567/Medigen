from datetime import date, time, timedelta

from app.core.enums import InventoryStatus, NotificationStatus
from app.repositories.dashboard_repository import DashboardRepository
from tests.support import (
    create_inventory_item,
    create_medicine,
    create_notification,
    create_schedule,
    create_user,
)


def test_dashboard_repository_returns_expected_dashboard_data(db_session):
    today = date(2026, 7, 12)
    user = create_user(db_session)
    medicine = create_medicine(db_session)

    create_notification(db_session, user_id=user.id, status=NotificationStatus.PENDING)
    create_notification(db_session, user_id=user.id, status=NotificationStatus.SENT)
    create_notification(db_session, user_id=user.id, status=NotificationStatus.READ)

    create_schedule(
        db_session,
        user_id=user.id,
        medicine_id=medicine.id,
        start_date=today,
        reminder_time=time(9, 0),
    )
    create_schedule(
        db_session,
        user_id=user.id,
        medicine_id=medicine.id,
        start_date=today - timedelta(days=2),
        end_date=today + timedelta(days=2),
        reminder_time=time(7, 30),
    )
    create_schedule(
        db_session,
        user_id=user.id,
        medicine_id=medicine.id,
        start_date=today + timedelta(days=1),
        reminder_time=time(11, 0),
    )

    create_inventory_item(db_session, user_id=user.id, medicine_id=medicine.id)
    create_inventory_item(
        db_session,
        user_id=user.id,
        medicine_id=medicine.id,
        status=InventoryStatus.EXPIRING_SOON,
    )

    repository = DashboardRepository(db_session)

    fetched_user = repository.get_user_by_id(user.id)
    notification_count = repository.get_unread_notification_count(user.id)
    schedule = repository.get_todays_schedule(user.id, today)
    inventory_summary = repository.get_inventory_summary(user.id)

    assert fetched_user is not None
    assert fetched_user.id == user.id
    assert notification_count == 2
    assert [item.reminder_time for item in schedule] == [time(7, 30), time(9, 0)]
    assert inventory_summary == {"total_medicines": 2, "expiring_soon": 1}


def test_dashboard_repository_returns_empty_results_when_no_data_exists(db_session):
    today = date(2026, 7, 12)
    user = create_user(db_session, email="empty@example.com")
    repository = DashboardRepository(db_session)

    assert repository.get_unread_notification_count(user.id) == 0
    assert repository.get_todays_schedule(user.id, today) == []
    assert repository.get_inventory_summary(user.id) == {
        "total_medicines": 0,
        "expiring_soon": 0,
    }

