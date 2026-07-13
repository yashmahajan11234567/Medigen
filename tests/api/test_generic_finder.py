from app.auth.jwt import create_access_token
from app.core.constants import NO_EXACT_GENERIC_SUBSTITUTE_FOUND
from app.core.enums import MedicineType
from tests.support import create_medicine, create_user


def test_generic_search_api_returns_exact_matches(client, db_session):
    create_medicine(
        db_session,
        name="Crocin 500",
        generic_name="Paracetamol",
        brand_name="Crocin 500",
        composition="Paracetamol",
        strength="500",
        unit="mg",
        dosage_form=MedicineType.TABLET,
        route="oral",
    )
    create_medicine(
        db_session,
        name="Paracetamol Generic",
        generic_name="Paracetamol",
        composition="Paracetamol",
        strength="500",
        unit="mg",
        dosage_form=MedicineType.TABLET,
        route="oral",
    )

    response = client.get("/api/v1/generic/search", params={"brand_name": "Crocin 500"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["source_medicine"]["brand_name"] == "Crocin 500"
    assert len(payload["matches"]) == 1
    assert payload["matches"][0]["name"] == "Paracetamol Generic"


def test_generic_search_api_returns_no_exact_match_message(client, db_session):
    create_medicine(
        db_session,
        name="Crocin 500",
        generic_name="Paracetamol",
        brand_name="Crocin 500",
        composition="Paracetamol",
        strength="500",
        unit="mg",
        dosage_form=MedicineType.TABLET,
        route="oral",
    )

    response = client.get("/api/v1/generic/search", params={"brand_name": "Crocin 500"})

    assert response.status_code == 200
    assert response.json()["message"] == NO_EXACT_GENERIC_SUBSTITUTE_FOUND


def test_generic_scan_api_rejects_approximate_match(client, db_session):
    create_medicine(
        db_session,
        name="Paracetamol 650 Generic",
        generic_name="Paracetamol",
        composition="Paracetamol",
        strength="650",
        unit="mg",
        dosage_form=MedicineType.TABLET,
        route="oral",
    )

    response = client.post(
        "/api/v1/generic/scan",
        json={
            "ingredient": "Paracetamol",
            "strength": "500",
            "unit": "mg",
            "dosage_form": "tablet",
            "route": "oral",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["matches"] == []
    assert payload["message"] == NO_EXACT_GENERIC_SUBSTITUTE_FOUND


def test_generic_details_api_returns_medicine_details(client, db_session):
    medicine = create_medicine(
        db_session,
        name="Paracetamol Generic",
        generic_name="Paracetamol",
        composition="Paracetamol",
        strength="500",
        unit="mg",
        dosage_form=MedicineType.TABLET,
        route="oral",
    )

    response = client.get(f"/api/v1/generic/{medicine.id}")

    assert response.status_code == 200
    assert response.json()["medicine"]["id"] == medicine.id
    assert response.json()["is_generic"] is True


def test_add_to_inventory_api_requires_auth_and_adds_the_medicine(client, db_session):
    user = create_user(db_session, email="inventory-link@example.com")
    medicine = create_medicine(
        db_session,
        name="Paracetamol Generic",
        generic_name="Paracetamol",
        composition="Paracetamol",
        strength="500",
        unit="mg",
        dosage_form=MedicineType.TABLET,
        route="oral",
    )

    unauthenticated = client.post(
        "/api/v1/generic/add-to-inventory",
        json={"medicine_id": medicine.id},
    )
    token = create_access_token(subject=str(user.id))
    authenticated = client.post(
        "/api/v1/generic/add-to-inventory",
        json={"medicine_id": medicine.id},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert unauthenticated.status_code == 401
    assert authenticated.status_code == 200
    assert authenticated.json()["message"] == "Medicine added to inventory."
