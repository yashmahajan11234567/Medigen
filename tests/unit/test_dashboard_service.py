from datetime import date, datetime, time

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppException
from app.services.dashboard_service import DashboardService
from tests.support import (
    create_inventory_item,
    create_medicine,
    create_notification,
    create_schedule,
    create_user,
)


@pytest.mark.parametrize(
    ("hour", "expected_greeting"),
    [
        (5, "Good Morning"),
        (12, "Good Afternoon"),
        (17, "Good Evening"),
        (22, "Good Night"),
        (2, "Good Night"),
    ],
)
def test_dashboard_service_greeting_logic(db_session, hour, expected_greeting):
    service = DashboardService(db_session)

    greeting = service.get_greeting(datetime(2026, 7, 12, hour, 0, 0))

    assert greeting == expected_greeting


def test_dashboard_service_aggregates_dashboard_data(db_session):
    user = create_user(db_session, email="aggregate@example.com")
    medicine = create_medicine(db_session)
    create_notification(db_session, user_id=user.id)
    create_schedule(
        db_session,
        user_id=user.id,
        medicine_id=medicine.id,
        start_date=date(2026, 7, 12),
        reminder_time=time(8, 45),
    )
    create_inventory_item(db_session, user_id=user.id, medicine_id=medicine.id)

    service = DashboardService(db_session)
    dashboard = service.get_dashboard(user.id, datetime(2026, 7, 12, 8, 0, 0))

    assert dashboard.user.name == "Dashboard User"
    assert dashboard.greeting == "Good Morning"
    assert dashboard.notification_count == 1
    assert len(dashboard.today_schedule) == 1
    assert dashboard.today_schedule[0].medicine_name == medicine.name
    assert dashboard.inventory_summary.total_medicines == 1
    assert dashboard.inventory_summary.expiring_soon == 0


def test_dashboard_service_returns_empty_collections_without_errors(db_session):
    user = create_user(db_session, email="empty-service@example.com")
    service = DashboardService(db_session)

    dashboard = service.get_dashboard(user.id, datetime(2026, 7, 12, 14, 0, 0))

    assert dashboard.greeting == "Good Afternoon"
    assert dashboard.notification_count == 0
    assert dashboard.today_schedule == []
    assert dashboard.inventory_summary.total_medicines == 0


def test_dashboard_service_raises_not_found_when_user_is_missing(db_session):
    service = DashboardService(db_session)

    with pytest.raises(AppException) as exc_info:
        service.get_dashboard(999, datetime(2026, 7, 12, 10, 0, 0))

    assert exc_info.value.status_code == 404
    assert exc_info.value.code == "dashboard_user_not_found"


def test_dashboard_service_translates_database_errors(db_session):
    service = DashboardService(db_session)

    class FailingRepository:
        def get_user_by_id(self, user_id: int):
            raise SQLAlchemyError("boom")

    service.repository = FailingRepository()

    with pytest.raises(AppException) as exc_info:
        service.get_dashboard(1, datetime(2026, 7, 12, 10, 0, 0))

    assert exc_info.value.status_code == 500
    assert exc_info.value.code == "database_error"

