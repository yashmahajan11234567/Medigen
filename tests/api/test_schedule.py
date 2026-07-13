from datetime import date, timedelta

from app.auth.jwt import create_access_token
from app.core.enums import MedicineType
from tests.support import create_medicine, create_user


def test_schedule_api_crud_today_bill_and_complete(client, db_session):
    user = create_user(db_session, email="schedule-api@example.com")
    token = create_access_token(subject=str(user.id))
    medicine = create_medicine(db_session, name="Schedule API Med", dosage_form=MedicineType.TABLET)
    bill_medicine = create_medicine(
        db_session,
        name="Crocin 500",
        brand_name="Crocin 500",
        generic_name="Paracetamol",
        dosage_form=MedicineType.TABLET,
    )

    create_response = client.post(
        "/api/v1/schedule",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "medicine_id": medicine.id,
            "dosage_pattern": "1-0-1",
            "food_timing": "after_food",
            "start_date": str(date.today()),
            "duration_days": 2,
            "quantity": 10,
            "quantity_unit": "tablets",
        },
    )
    created_id = create_response.json()["id"]
    reminder_id = create_response.json()["reminders"][0]["id"]

    list_response = client.get("/api/v1/schedule", headers={"Authorization": f"Bearer {token}"})
    detail_response = client.get(f"/api/v1/schedule/{created_id}", headers={"Authorization": f"Bearer {token}"})
    today_response = client.get("/api/v1/schedule/today", headers={"Authorization": f"Bearer {token}"})
    update_response = client.put(
        f"/api/v1/schedule/{created_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "dosage_pattern": "0-1-0",
            "food_timing": "before_food",
            "duration_days": 2,
            "quantity": 8,
            "quantity_unit": "tablets",
        },
    )
    updated_reminder_id = update_response.json()["reminders"][0]["id"]
    complete_response = client.post(
        "/api/v1/schedule/complete",
        headers={"Authorization": f"Bearer {token}"},
        json={"reminder_id": updated_reminder_id},
    )
    bill_response = client.post(
        "/api/v1/schedule/from-bill",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "medicine_name": bill_medicine.brand_name,
            "quantity": 6,
            "purchase_date": str(date.today()),
            "expiry_date": str(date.today() + timedelta(days=30)),
            "pharmacy_name": "Apollo",
            "dosage_pattern": "1-0-0",
            "food_timing": "after_food",
            "start_date": str(date.today()),
            "duration_days": 3,
        },
    )
    delete_response = client.delete(
        f"/api/v1/schedule/{created_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert create_response.status_code == 201
    assert list_response.status_code == 200
    assert len(list_response.json()["items"]) >= 1
    assert detail_response.status_code == 200
    assert today_response.status_code == 200
    assert len(today_response.json()["items"]) >= 1
    assert update_response.status_code == 200
    assert complete_response.status_code == 200
    assert complete_response.json()["completed_at"] is not None
    assert bill_response.status_code == 201
    assert delete_response.status_code == 200


def test_schedule_api_rejects_invalid_dosage_and_requires_auth(client, db_session):
    user = create_user(db_session, email="schedule-invalid@example.com")
    token = create_access_token(subject=str(user.id))
    medicine = create_medicine(db_session, name="Invalid Med", dosage_form=MedicineType.TABLET)

    unauthenticated = client.get("/api/v1/schedule")
    invalid = client.post(
        "/api/v1/schedule",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "medicine_id": medicine.id,
            "dosage_pattern": "1-1",
            "food_timing": "after_food",
            "start_date": str(date.today()),
            "duration_days": 1,
            "quantity": 2,
            "quantity_unit": "tablets",
        },
    )

    assert unauthenticated.status_code == 401
    assert invalid.status_code == 422
