from datetime import date

from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppException
from app.core.enums import MedicalRecordDocumentType
from app.models.medical_record import MedicalRecord, MedicalRecordDocument
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.medical_record_repository import MedicalRecordRepository
from app.repositories.medicine_repository import MedicineRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.schemas.medical_records import (
    MedicalRecordCreateRequest,
    MedicalRecordDeleteResponse,
    MedicalRecordDocumentResponse,
    MedicalRecordLinkRequest,
    MedicalRecordListResponse,
    MedicalRecordResponse,
    MedicalRecordUpdateRequest,
)
from app.utils.datetime import utc_now


class MedicalRecordService:
    def __init__(self, session) -> None:
        self.session = session
        self.repository = MedicalRecordRepository(session)
        self.schedule_repository = ScheduleRepository(session)
        self.inventory_repository = InventoryRepository(session)
        self.medicine_repository = MedicineRepository(session)

    def create_record(self, *, user_id: int, payload: MedicalRecordCreateRequest) -> MedicalRecordResponse:
        self._validate_record_dates(payload.visit_date)
        link_targets = self._resolve_link_targets(
            user_id=user_id,
            schedule_ids=payload.linked_schedule_ids,
            inventory_item_ids=payload.linked_inventory_item_ids,
            medicine_ids=payload.linked_medicine_ids,
        )
        record = MedicalRecord(
            user_id=user_id,
            title=payload.title,
            folder_name=payload.folder_name,
            description=payload.description,
            hospital_name=payload.hospital_name,
            doctor_name=payload.doctor_name,
            visit_date=payload.visit_date,
            diagnosis=payload.diagnosis,
            treatment_name=payload.treatment_name,
            notes=payload.notes,
            linked_generic_search_ids=payload.linked_generic_search_ids,
        )
        record.schedules.extend(link_targets["schedules"])
        record.inventory_items.extend(link_targets["inventory_items"])
        record.medicines.extend(link_targets["medicines"])
        documents = self._build_documents(payload.documents)

        try:
            created = self.repository.create_record(record, documents)
            refreshed = self.repository.get_record(user_id=user_id, record_id=created.id)
            if refreshed is None:
                raise AppException("Record not found.", 404, "record_not_found")
            return self._to_response(refreshed)
        except SQLAlchemyError as exc:
            raise AppException("Database failure while creating medical record.", 500, "database_failure") from exc

    def update_record(self, *, user_id: int, record_id: int, payload: MedicalRecordUpdateRequest) -> MedicalRecordResponse:
        try:
            record = self._get_record_or_raise(user_id=user_id, record_id=record_id)
            if "title" in payload.model_fields_set:
                record.title = payload.title
            if "folder_name" in payload.model_fields_set:
                record.folder_name = payload.folder_name
            if "description" in payload.model_fields_set:
                record.description = payload.description
            if "hospital_name" in payload.model_fields_set:
                record.hospital_name = payload.hospital_name
            if "doctor_name" in payload.model_fields_set:
                record.doctor_name = payload.doctor_name
            if "visit_date" in payload.model_fields_set:
                self._validate_record_dates(payload.visit_date)
                record.visit_date = payload.visit_date
            if "diagnosis" in payload.model_fields_set:
                record.diagnosis = payload.diagnosis
            if "treatment_name" in payload.model_fields_set:
                record.treatment_name = payload.treatment_name
            if "notes" in payload.model_fields_set:
                record.notes = payload.notes
            if "linked_generic_search_ids" in payload.model_fields_set:
                record.linked_generic_search_ids = payload.linked_generic_search_ids

            updated = self.repository.update_record(record)
            if payload.documents:
                self._validate_documents(payload.documents, record_id=record.id)
                self.repository.add_documents(record.id, self._build_documents(payload.documents))
            refreshed = self.repository.get_record(user_id=user_id, record_id=updated.id)
            if refreshed is None:
                raise AppException("Record not found.", 404, "record_not_found")
            return self._to_response(refreshed)
        except SQLAlchemyError as exc:
            raise AppException("Database failure while updating medical record.", 500, "database_failure") from exc

    def delete_record(self, *, user_id: int, record_id: int) -> MedicalRecordDeleteResponse:
        try:
            record = self._get_record_or_raise(user_id=user_id, record_id=record_id)
            self.repository.delete_record(record)
            return MedicalRecordDeleteResponse(message="Medical record deleted successfully.")
        except SQLAlchemyError as exc:
            raise AppException("Database failure while deleting medical record.", 500, "database_failure") from exc

    def get_record(self, *, user_id: int, record_id: int) -> MedicalRecordResponse:
        try:
            record = self._get_record_or_raise(user_id=user_id, record_id=record_id)
            return self._to_response(record)
        except SQLAlchemyError as exc:
            raise AppException("Database failure while loading medical record.", 500, "database_failure") from exc

    def list_records(self, *, user_id: int) -> MedicalRecordListResponse:
        try:
            records = self.repository.list_records(user_id=user_id)
            return MedicalRecordListResponse(items=[self._to_response(record) for record in records])
        except SQLAlchemyError as exc:
            raise AppException("Database failure while loading medical records.", 500, "database_failure") from exc

    def search_records(self, *, user_id: int, query: str) -> MedicalRecordListResponse:
        try:
            records = self.repository.search_records(user_id=user_id, query=query)
            return MedicalRecordListResponse(items=[self._to_response(record) for record in records])
        except SQLAlchemyError as exc:
            raise AppException("Database failure while searching medical records.", 500, "database_failure") from exc

    def filter_records(
        self,
        *,
        user_id: int,
        document_type: MedicalRecordDocumentType | None = None,
        hospital: str | None = None,
        date_from=None,
        date_to=None,
    ) -> MedicalRecordListResponse:
        if date_from and date_to and date_to < date_from:
            raise AppException("Invalid dates.", 422, "invalid_dates")
        try:
            records = self.repository.filter_records(
                user_id=user_id,
                document_type=document_type,
                hospital=hospital,
                date_from=date_from,
                date_to=date_to,
            )
            return MedicalRecordListResponse(items=[self._to_response(record) for record in records])
        except SQLAlchemyError as exc:
            raise AppException("Database failure while filtering medical records.", 500, "database_failure") from exc

    def link_modules(self, *, user_id: int, payload: MedicalRecordLinkRequest) -> MedicalRecordResponse:
        try:
            record = self._get_record_or_raise(user_id=user_id, record_id=payload.record_id)
            linked = self._apply_links(
                record=record,
                link_targets=self._resolve_link_targets(
                    user_id=user_id,
                    schedule_ids=payload.schedule_ids,
                    inventory_item_ids=payload.inventory_item_ids,
                    medicine_ids=payload.medicine_ids,
                ),
            )
            refreshed = self.repository.get_record(user_id=user_id, record_id=linked.id)
            if refreshed is None:
                raise AppException("Record not found.", 404, "record_not_found")
            return self._to_response(refreshed)
        except SQLAlchemyError as exc:
            raise AppException("Database failure while linking medical record.", 500, "database_failure") from exc

    def _apply_links(self, *, record, link_targets: dict[str, list]):
        for schedule in link_targets["schedules"]:
            record = self.repository.link_schedule(record, schedule)
        for inventory_item in link_targets["inventory_items"]:
            record = self.repository.link_inventory(record, inventory_item)
        for medicine in link_targets["medicines"]:
            record = self.repository.link_medicine(record, medicine)
        return record

    def _resolve_link_targets(
        self,
        *,
        user_id: int,
        schedule_ids: list[int],
        inventory_item_ids: list[int],
        medicine_ids: list[int],
    ) -> dict[str, list]:
        schedules = []
        seen_schedule_ids: set[int] = set()
        for schedule_id in schedule_ids:
            if schedule_id in seen_schedule_ids:
                continue
            seen_schedule_ids.add(schedule_id)
            schedule = self.schedule_repository.get_schedule_by_id(user_id=user_id, schedule_id=schedule_id)
            if schedule is None:
                raise AppException("Invalid links: unknown schedule ID.", 422, "invalid_links")
            schedules.append(schedule)

        inventory_items = []
        seen_inventory_ids: set[int] = set()
        for inventory_item_id in inventory_item_ids:
            if inventory_item_id in seen_inventory_ids:
                continue
            seen_inventory_ids.add(inventory_item_id)
            inventory_item = self.inventory_repository.get_inventory_item_by_id(user_id=user_id, inventory_id=inventory_item_id)
            if inventory_item is None:
                raise AppException("Invalid links: unknown inventory item ID.", 422, "invalid_links")
            inventory_items.append(inventory_item)

        medicines = []
        seen_medicine_ids: set[int] = set()
        for medicine_id in medicine_ids:
            if medicine_id in seen_medicine_ids:
                continue
            seen_medicine_ids.add(medicine_id)
            medicine = self.medicine_repository.get_medicine_by_id(medicine_id)
            if medicine is None:
                raise AppException("Invalid links: unknown medicine ID.", 422, "invalid_links")
            medicines.append(medicine)

        return {
            "schedules": schedules,
            "inventory_items": inventory_items,
            "medicines": medicines,
        }

    def _get_record_or_raise(self, *, user_id: int, record_id: int):
        record = self.repository.get_record(user_id=user_id, record_id=record_id)
        if record is None:
            raise AppException("Record not found.", 404, "record_not_found")
        return record

    def _validate_record_dates(self, visit_date: date | None):
        return visit_date

    def _validate_documents(self, documents, record_id: int | None = None):
        seen_paths: set[str] = set()
        for document in documents:
            if document.storage_path in seen_paths:
                raise AppException("Duplicate document.", 409, "duplicate_document")
            seen_paths.add(document.storage_path)
            if record_id is not None and self.repository.get_document_by_storage_path(record_id=record_id, storage_path=document.storage_path):
                raise AppException("Duplicate document.", 409, "duplicate_document")

    def _build_documents(self, documents) -> list[MedicalRecordDocument]:
        self._validate_documents(documents)
        built: list[MedicalRecordDocument] = []
        for document in documents:
            built.append(
                MedicalRecordDocument(
                    document_type=document.document_type,
                    file_name=document.file_name,
                    file_path=document.storage_path,
                    storage_path=document.storage_path,
                    file_type=document.file_type,
                    file_size=document.file_size,
                    upload_date=document.upload_date or utc_now(),
                    mime_type=document.file_type,
                    doctor_name=document.doctor_name,
                    hospital_or_clinic=document.hospital_or_clinic,
                    doctor_specialty=document.doctor_specialty,
                    consultation_date=document.consultation_date,
                    follow_up_date=document.follow_up_date,
                    diagnosis=document.diagnosis,
                    notes=document.notes,
                )
            )
        return built

    def _to_response(self, record) -> MedicalRecordResponse:
        documents = [
            MedicalRecordDocumentResponse(
                id=document.id,
                document_type=document.document_type,
                file_name=document.file_name,
                file_type=document.file_type,
                file_size=document.file_size,
                storage_path=document.storage_path,
                upload_date=document.upload_date,
                doctor_name=document.doctor_name,
                hospital_or_clinic=document.hospital_or_clinic,
                doctor_specialty=document.doctor_specialty,
                consultation_date=document.consultation_date,
                follow_up_date=document.follow_up_date,
                diagnosis=document.diagnosis,
                notes=document.notes,
            )
            for document in record.documents
            if not document.is_deleted
        ]
        return MedicalRecordResponse(
            id=record.id,
            title=record.title,
            folder_name=record.folder_name,
            description=record.description,
            hospital_name=record.hospital_name,
            doctor_name=record.doctor_name,
            visit_date=record.visit_date,
            diagnosis=record.diagnosis,
            treatment_name=record.treatment_name,
            notes=record.notes,
            documents=documents,
            linked_schedule_ids=[schedule.id for schedule in record.schedules if not schedule.is_deleted],
            linked_inventory_item_ids=[item.id for item in record.inventory_items if not item.is_deleted],
            linked_medicine_ids=[medicine.id for medicine in record.medicines if not medicine.is_deleted],
            linked_generic_search_ids=record.linked_generic_search_ids or [],
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
