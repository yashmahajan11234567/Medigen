from datetime import date

from sqlalchemy.exc import SQLAlchemyError

from app.auth.jwt import create_access_token
from app.repositories import medical_record_repository as medical_record_repository_module
from app.repositories.medical_record_repository import MedicalRecordRepository
from tests.support import (
    create_inventory_item,
    create_medicine,
    create_medical_record,
    create_schedule,
    create_user,
)


def test_medical_records_api_crud_search_filter_and_link(client, db_session):
    user = create_user(db_session, email="records-api@example.com")
    medicine = create_medicine(db_session, name="API Record Med")
    schedule = create_schedule(
        db_session,
        user_id=user.id,
        medicine_id=medicine.id,
        start_date=date(2026, 7, 13),
    )
    inventory_item = create_inventory_item(db_session, user_id=user.id, medicine_id=medicine.id)
    token = create_access_token(subject=str(user.id))

    create_response = client.post(
        "/api/v1/medical-records",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Orthopedic Visit",
            "folder_name": "Orthopedics",
            "description": "Knee pain treatment",
            "hospital_name": "Metro Clinic",
            "doctor_name": "Dr. Khan",
            "visit_date": "2026-07-12",
            "diagnosis": "Knee strain",
            "treatment_name": "Physiotherapy",
            "notes": "Need exercise plan",
            "linked_schedule_ids": [schedule.id],
            "linked_inventory_item_ids": [inventory_item.id],
            "linked_medicine_ids": [medicine.id],
            "documents": [
                {
                    "document_type": "prescription",
                    "file_name": "orthopedic.pdf",
                    "file_type": "application/pdf",
                    "file_size": 2048,
                    "storage_path": "/records/orthopedics/orthopedic.pdf",
                }
            ],
        },
    )
    created_id = create_response.json()["id"]

    list_response = client.get("/api/v1/medical-records", headers={"Authorization": f"Bearer {token}"})
    detail_response = client.get(
        f"/api/v1/medical-records/{created_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    search_response = client.get(
        "/api/v1/medical-records/search",
        headers={"Authorization": f"Bearer {token}"},
        params={"query": "ortho"},
    )
    filter_response = client.get(
        "/api/v1/medical-records/filter",
        headers={"Authorization": f"Bearer {token}"},
        params={"document_type": "prescription", "hospital": "metro"},
    )
    update_response = client.put(
        f"/api/v1/medical-records/{created_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Orthopedic Follow-up", "notes": None},
    )
    link_response = client.post(
        "/api/v1/medical-records/link",
        headers={"Authorization": f"Bearer {token}"},
        json={"record_id": created_id, "medicine_ids": [medicine.id]},
    )
    delete_response = client.delete(
        f"/api/v1/medical-records/{created_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert create_response.status_code == 201
    assert list_response.status_code == 200
    assert len(list_response.json()["items"]) == 1
    assert detail_response.status_code == 200
    assert detail_response.json()["linked_schedule_ids"] == [schedule.id]
    assert search_response.status_code == 200
    assert len(search_response.json()["items"]) == 1
    assert filter_response.status_code == 200
    assert len(filter_response.json()["items"]) == 1
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Orthopedic Follow-up"
    assert update_response.json()["notes"] is None
    assert link_response.status_code == 200
    assert link_response.json()["linked_medicine_ids"] == [medicine.id]
    assert delete_response.status_code == 200


def test_medical_records_api_handles_validation_and_not_found(client, db_session):
    user = create_user(db_session, email="records-api-validation@example.com")
    token = create_access_token(subject=str(user.id))

    invalid_create = client.post(
        "/api/v1/medical-records",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": " ",
            "folder_name": "Validation",
        },
    )
    invalid_filter = client.get(
        "/api/v1/medical-records/filter",
        headers={"Authorization": f"Bearer {token}"},
        params={"date_from": "2026-07-20", "date_to": "2026-07-10"},
    )
    missing_record = client.get(
        "/api/v1/medical-records/999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert invalid_create.status_code == 422
    assert invalid_create.json()["code"] == "validation_error"
    assert invalid_filter.status_code == 422
    assert invalid_filter.json()["code"] == "invalid_dates"
    assert missing_record.status_code == 404
    assert missing_record.json()["code"] == "record_not_found"


def test_medical_records_api_requires_authentication(client):
    response = client.get("/api/v1/medical-records")

    assert response.status_code == 401


def test_medical_records_api_returns_database_failure_response(client, db_session, monkeypatch):
    user = create_user(db_session, email="records-api-db@example.com")
    create_medical_record(db_session, user_id=user.id, title="DB Failure", folder_name="DB Failure")
    token = create_access_token(subject=str(user.id))

    original_method = MedicalRecordRepository.list_records

    def failing_list_records(self, *, user_id: int):
        raise SQLAlchemyError("db failed")

    monkeypatch.setattr(
        medical_record_repository_module.MedicalRecordRepository,
        "list_records",
        failing_list_records,
    )

    response = client.get(
        "/api/v1/medical-records",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 500
    assert response.json()["code"] == "database_failure"
    assert response.json()["message"] == "Database failure while loading medical records."

    monkeypatch.setattr(
        medical_record_repository_module.MedicalRecordRepository,
        "list_records",
        original_method,
    )

