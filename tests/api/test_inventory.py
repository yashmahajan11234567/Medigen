from datetime import date, timedelta

from app.auth.jwt import create_access_token
from app.core.enums import MedicineType
from tests.support import create_inventory_item, create_medicine, create_user


def test_inventory_api_crud_search_filter_and_summary(client, db_session):
    user = create_user(db_session, email="inventory-api@example.com")
    token = create_access_token(subject=str(user.id))

    create_response = client.post(
        "/api/v1/inventory",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Paracetamol 500",
            "generic_name": "Paracetamol",
            "type": "tablet",
            "quantity": 12,
            "quantity_unit": "tablets",
            "expiry_date": str(date.today() + timedelta(days=40)),
        },
    )
    created_id = create_response.json()["id"]

    list_response = client.get("/api/v1/inventory", headers={"Authorization": f"Bearer {token}"})
    detail_response = client.get(f"/api/v1/inventory/{created_id}", headers={"Authorization": f"Bearer {token}"})
    search_response = client.get(
        "/api/v1/inventory/search",
        headers={"Authorization": f"Bearer {token}"},
        params={"query": "para"},
    )
    filter_response = client.get(
        "/api/v1/inventory/filter",
        headers={"Authorization": f"Bearer {token}"},
        params={"status": "available"},
    )
    update_response = client.put(
        f"/api/v1/inventory/{created_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"quantity": 3, "type": "tablet"},
    )
    summary_response = client.get(
        "/api/v1/inventory/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    delete_response = client.delete(
        f"/api/v1/inventory/{created_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert create_response.status_code == 201
    assert list_response.status_code == 200
    assert len(list_response.json()["items"]) == 1
    assert detail_response.status_code == 200
    assert search_response.status_code == 200
    assert len(search_response.json()["items"]) == 1
    assert filter_response.status_code == 200
    assert len(filter_response.json()["items"]) == 1
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "low_stock"
    assert summary_response.status_code == 200
    assert summary_response.json()["total_medicines"] == 1
    assert delete_response.status_code == 200


def test_inventory_api_handles_expired_and_finished_filters(client, db_session):
    user = create_user(db_session, email="inventory-filter-api@example.com")
    token = create_access_token(subject=str(user.id))
    tablet = create_medicine(db_session, name="Tablet A", dosage_form=MedicineType.TABLET)
    ointment = create_medicine(db_session, name="Ointment A", dosage_form=MedicineType.OINTMENT)
    create_inventory_item(
        db_session,
        user_id=user.id,
        medicine_id=tablet.id,
        quantity=0,
        expiry_date=date.today() + timedelta(days=100),
    )
    create_inventory_item(
        db_session,
        user_id=user.id,
        medicine_id=ointment.id,
        expiry_date=date.today() - timedelta(days=1),
    )

    finished_response = client.get(
        "/api/v1/inventory/filter",
        headers={"Authorization": f"Bearer {token}"},
        params={"status": "finished"},
    )
    expired_response = client.get(
        "/api/v1/inventory/filter",
        headers={"Authorization": f"Bearer {token}"},
        params={"status": "expired", "type": "ointment"},
    )

    assert finished_response.status_code == 200
    assert len(finished_response.json()["items"]) == 1
    assert expired_response.status_code == 200
    assert len(expired_response.json()["items"]) == 1


def test_inventory_api_requires_authentication(client):
    response = client.get("/api/v1/inventory")

    assert response.status_code == 401


def test_generic_finder_inventory_integration_now_succeeds(client, db_session):
    user = create_user(db_session, email="generic-integration@example.com")
    token = create_access_token(subject=str(user.id))
    medicine = create_medicine(
        db_session,
        name="Paracetamol Generic",
        generic_name="Paracetamol",
        dosage_form=MedicineType.TABLET,
    )

    response = client.post(
        "/api/v1/generic/add-to-inventory",
        headers={"Authorization": f"Bearer {token}"},
        json={"medicine_id": medicine.id},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Medicine added to inventory."

