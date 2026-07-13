from datetime import date, time

from sqlalchemy.exc import SQLAlchemyError

from app.auth.jwt import create_access_token
from app.repositories import dashboard_repository as dashboard_repository_module
from app.repositories.dashboard_repository import DashboardRepository
from tests.support import (
    create_inventory_item,
    create_medicine,
    create_notification,
    create_schedule,
    create_user,
)


def test_dashboard_api_returns_aggregated_response(client, db_session):
    user = create_user(db_session, email="api-dashboard@example.com")
    medicine = create_medicine(db_session, name="Azithromycin 500")
    create_notification(db_session, user_id=user.id)
    create_schedule(
        db_session,
        user_id=user.id,
        medicine_id=medicine.id,
        start_date=date(2026, 7, 12),
        reminder_time=time(9, 30),
    )
    create_inventory_item(db_session, user_id=user.id, medicine_id=medicine.id)
    token = create_access_token(subject=str(user.id))

    response = client.get(
        "/api/v1/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["user"]["id"] == user.id
    assert payload["user"]["name"] == user.full_name
    assert payload["notification_count"] == 1
    assert payload["today_schedule"][0]["medicine_name"] == "Azithromycin 500"
    assert payload["inventory_summary"] == {"total_medicines": 1, "expiring_soon": 0}


def test_dashboard_api_requires_authentication(client):
    response = client.get("/api/v1/dashboard")

    assert response.status_code == 401
    assert response.json()["message"] == "Authentication credentials were not provided."


def test_dashboard_api_handles_empty_dashboard_state(client, db_session):
    user = create_user(db_session, email="empty-api@example.com")
    token = create_access_token(subject=str(user.id))

    response = client.get(
        "/api/v1/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["notification_count"] == 0
    assert payload["today_schedule"] == []
    assert payload["inventory_summary"] == {"total_medicines": 0, "expiring_soon": 0}


def test_dashboard_api_returns_database_error_response(client, db_session, monkeypatch):
    user = create_user(db_session, email="dberror-api@example.com")
    token = create_access_token(subject=str(user.id))

    original_method = DashboardRepository.get_user_by_id

    def failing_get_user_by_id(self, user_id: int):
        raise SQLAlchemyError("dashboard read failed")

    monkeypatch.setattr(
        dashboard_repository_module.DashboardRepository,
        "get_user_by_id",
        failing_get_user_by_id,
    )

    response = client.get(
        "/api/v1/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 500
    assert response.json()["code"] == "database_error"
    assert response.json()["message"] == "A database error occurred while loading the dashboard."

    monkeypatch.setattr(
        dashboard_repository_module.DashboardRepository,
        "get_user_by_id",
        original_method,
    )

