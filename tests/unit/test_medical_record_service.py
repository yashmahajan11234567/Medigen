from datetime import date

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.core.enums import MedicalRecordDocumentType
from app.core.exceptions import AppException
from app.schemas.medical_records import (
    MedicalRecordCreateRequest,
    MedicalRecordLinkRequest,
    MedicalRecordUpdateRequest,
)
from app.services.medical_record_service import MedicalRecordService
from tests.support import (
    create_inventory_item,
    create_medicine,
    create_medical_record,
    create_medical_record_document,
    create_schedule,
    create_user,
)


def test_medical_record_service_crud_search_filter_and_linking(db_session):
    user = create_user(db_session, email="records-service@example.com")
    medicine = create_medicine(db_session, name="Service Med")
    schedule = create_schedule(
        db_session,
        user_id=user.id,
        medicine_id=medicine.id,
        start_date=date(2026, 7, 13),
    )
    inventory_item = create_inventory_item(db_session, user_id=user.id, medicine_id=medicine.id)
    service = MedicalRecordService(db_session)

    created = service.create_record(
        user_id=user.id,
        payload=MedicalRecordCreateRequest(
            title="Neurology Visit",
            folder_name="Neurology",
            hospital_name="Metro Hospital",
            doctor_name="Dr. Rao",
            visit_date=date(2026, 7, 12),
            diagnosis="Migraine",
            treatment_name="Medication",
            notes="Needs review",
            linked_schedule_ids=[schedule.id],
            linked_inventory_item_ids=[inventory_item.id],
            linked_medicine_ids=[medicine.id],
            linked_generic_search_ids=["search-1"],
            documents=[
                {
                    "document_type": "prescription",
                    "file_name": "visit.pdf",
                    "file_type": "application/pdf",
                    "file_size": 1024,
                    "storage_path": "/records/neuro/visit.pdf",
                }
            ],
        ),
    )
    fetched = service.get_record(user_id=user.id, record_id=created.id)
    updated = service.update_record(
        user_id=user.id,
        record_id=created.id,
        payload=MedicalRecordUpdateRequest(
            title="Neurology Follow-up",
            notes=None,
            documents=[
                {
                    "document_type": "other_document",
                    "file_name": "scan.pdf",
                    "file_type": "application/pdf",
                    "file_size": 2048,
                    "storage_path": "/records/neuro/scan.pdf",
                }
            ],
        ),
    )
    searched = service.search_records(user_id=user.id, query="neurology")
    filtered = service.filter_records(
        user_id=user.id,
        document_type=MedicalRecordDocumentType.PRESCRIPTION,
        hospital="metro",
        date_from=date(2026, 7, 1),
        date_to=date(2026, 7, 31),
    )
    linked = service.link_modules(
        user_id=user.id,
        payload=MedicalRecordLinkRequest(record_id=created.id, medicine_ids=[medicine.id]),
    )
    listed = service.list_records(user_id=user.id)
    deleted = service.delete_record(user_id=user.id, record_id=created.id)

    assert fetched.linked_schedule_ids == [schedule.id]
    assert fetched.linked_inventory_item_ids == [inventory_item.id]
    assert fetched.linked_medicine_ids == [medicine.id]
    assert fetched.linked_generic_search_ids == ["search-1"]
    assert updated.title == "Neurology Follow-up"
    assert updated.notes is None
    assert len(updated.documents) == 2
    assert [item.id for item in searched.items] == [created.id]
    assert [item.id for item in filtered.items] == [created.id]
    assert linked.linked_medicine_ids == [medicine.id]
    assert len(listed.items) == 1
    assert deleted.message == "Medical record deleted successfully."
    assert service.list_records(user_id=user.id).items == []


def test_medical_record_service_rejects_unknown_links_and_duplicate_documents(db_session):
    user = create_user(db_session, email="records-validation@example.com")
    service = MedicalRecordService(db_session)

    with pytest.raises(AppException) as invalid_link_exc:
        service.create_record(
            user_id=user.id,
            payload=MedicalRecordCreateRequest(
                title="Bad Link",
                folder_name="Validation",
                linked_schedule_ids=[999],
            ),
        )

    assert invalid_link_exc.value.code == "invalid_links"

    record = create_medical_record(db_session, user_id=user.id, title="Duplicate Record", folder_name="Folder")
    create_medical_record_document(
        db_session,
        medical_record_id=record.id,
        document_type=MedicalRecordDocumentType.PRESCRIPTION,
        storage_path="/records/folder/duplicate.pdf",
    )

    with pytest.raises(AppException) as duplicate_exc:
        service.update_record(
            user_id=user.id,
            record_id=record.id,
            payload=MedicalRecordUpdateRequest(
                documents=[
                    {
                        "document_type": "other_document",
                        "file_name": "duplicate.pdf",
                        "file_type": "application/pdf",
                        "file_size": 512,
                        "storage_path": "/records/folder/duplicate.pdf",
                    }
                ]
            ),
        )

    assert duplicate_exc.value.code == "duplicate_document"


def test_medical_record_service_validates_filter_dates_and_missing_records(db_session):
    user = create_user(db_session, email="records-edge@example.com")
    service = MedicalRecordService(db_session)

    with pytest.raises(AppException) as invalid_dates_exc:
        service.filter_records(
            user_id=user.id,
            date_from=date(2026, 7, 20),
            date_to=date(2026, 7, 10),
        )

    with pytest.raises(AppException) as not_found_exc:
        service.get_record(user_id=user.id, record_id=999)

    assert invalid_dates_exc.value.code == "invalid_dates"
    assert not_found_exc.value.code == "record_not_found"


def test_medical_record_service_translates_database_errors(db_session):
    service = MedicalRecordService(db_session)

    class FailingRepository:
        def list_records(self, *, user_id: int):
            raise SQLAlchemyError("boom")

    service.repository = FailingRepository()

    with pytest.raises(AppException) as exc_info:
        service.list_records(user_id=1)

    assert exc_info.value.status_code == 500
    assert exc_info.value.code == "database_failure"

