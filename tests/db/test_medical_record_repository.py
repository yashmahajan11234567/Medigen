from datetime import date, time

from app.core.enums import MedicalRecordDocumentType
from app.models.medical_record import MedicalRecord, MedicalRecordDocument
from app.repositories.medical_record_repository import MedicalRecordRepository
from tests.support import (
    create_inventory_item,
    create_medicine,
    create_schedule,
    create_user,
)


def test_medical_record_repository_supports_crud_search_filter_and_linking(db_session):
    user = create_user(db_session, email="records-repo@example.com")
    medicine = create_medicine(db_session, name="Repo Record Med")
    schedule = create_schedule(
        db_session,
        user_id=user.id,
        medicine_id=medicine.id,
        start_date=date(2026, 7, 13),
        reminder_time=time(9, 0),
    )
    inventory_item = create_inventory_item(db_session, user_id=user.id, medicine_id=medicine.id)
    repository = MedicalRecordRepository(db_session)

    record = MedicalRecord(
        user_id=user.id,
        title="Cardiology Record",
        folder_name="Cardiology",
        hospital_name="City Hospital",
        doctor_name="Dr. Mehta",
        visit_date=date(2026, 7, 10),
        diagnosis="Hypertension",
        treatment_name="Observation",
        notes="Initial visit",
        linked_generic_search_ids=["generic-1"],
    )
    documents = [
        MedicalRecordDocument(
            document_type=MedicalRecordDocumentType.PRESCRIPTION,
            file_name="prescription.pdf",
            file_path="/records/cardio/prescription.pdf",
            storage_path="/records/cardio/prescription.pdf",
            file_type="application/pdf",
            file_size=2048,
            mime_type="application/pdf",
        )
    ]

    created = repository.create_record(record, documents)
    linked = repository.link_schedule(created, schedule)
    linked = repository.link_inventory(linked, inventory_item)
    linked = repository.link_medicine(linked, medicine)
    fetched = repository.get_record(user_id=user.id, record_id=linked.id)
    listed = repository.list_records(user_id=user.id)
    searched = repository.search_records(user_id=user.id, query="cardio")
    filtered = repository.filter_records(
        user_id=user.id,
        document_type=MedicalRecordDocumentType.PRESCRIPTION,
        hospital="city",
        date_from=date(2026, 7, 1),
        date_to=date(2026, 7, 31),
    )
    duplicate_document = repository.get_document_by_storage_path(
        record_id=created.id,
        storage_path="/records/cardio/prescription.pdf",
    )

    assert fetched is not None
    assert fetched.folder_name == "Cardiology"
    assert [item.id for item in fetched.schedules] == [schedule.id]
    assert [item.id for item in fetched.inventory_items] == [inventory_item.id]
    assert [item.id for item in fetched.medicines] == [medicine.id]
    assert len(listed) == 1
    assert [item.id for item in searched] == [created.id]
    assert [item.id for item in filtered] == [created.id]
    assert duplicate_document is not None

    repository.delete_record(fetched)

    assert repository.get_record(user_id=user.id, record_id=created.id) is None

