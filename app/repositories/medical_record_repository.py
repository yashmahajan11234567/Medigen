from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from app.models.inventory import InventoryItem
from app.models.medical_record import MedicalRecord, MedicalRecordDocument
from app.models.medicine import Medicine
from app.models.schedule import Schedule
from app.repositories.base import BaseRepository
from app.utils.datetime import utc_now


class MedicalRecordRepository(BaseRepository):
    def create_record(self, record: MedicalRecord, documents: list[MedicalRecordDocument]) -> MedicalRecord:
        self.session.add(record)
        self.session.flush()
        for document in documents:
            document.medical_record_id = record.id
            self.session.add(document)
        self.session.commit()
        self.session.refresh(record)
        return record

    def update_record(self, record: MedicalRecord) -> MedicalRecord:
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def add_documents(self, record_id: int, documents: list[MedicalRecordDocument]) -> None:
        for document in documents:
            document.medical_record_id = record_id
            self.session.add(document)
        self.session.commit()

    def delete_record(self, record: MedicalRecord) -> None:
        record.is_deleted = True
        record.deleted_at = utc_now()
        self.session.add(record)
        for document in record.documents:
            document.is_deleted = True
            document.deleted_at = utc_now()
            self.session.add(document)
        self.session.commit()

    def get_record(self, *, user_id: int, record_id: int) -> MedicalRecord | None:
        statement = (
            select(MedicalRecord)
            .execution_options(populate_existing=True)
            .options(
                selectinload(MedicalRecord.documents),
                selectinload(MedicalRecord.schedules),
                selectinload(MedicalRecord.inventory_items),
                selectinload(MedicalRecord.medicines),
            )
            .where(
                MedicalRecord.id == record_id,
                MedicalRecord.user_id == user_id,
                MedicalRecord.is_deleted.is_(False),
            )
        )
        return self.session.execute(statement).scalars().unique().one_or_none()

    def list_records(self, *, user_id: int) -> list[MedicalRecord]:
        statement = (
            select(MedicalRecord)
            .options(
                selectinload(MedicalRecord.documents),
                selectinload(MedicalRecord.schedules),
                selectinload(MedicalRecord.inventory_items),
                selectinload(MedicalRecord.medicines),
            )
            .where(
                MedicalRecord.user_id == user_id,
                MedicalRecord.is_deleted.is_(False),
            )
            .order_by(MedicalRecord.created_at.desc(), MedicalRecord.id.desc())
        )
        return list(self.session.execute(statement).scalars().unique().all())

    def search_records(self, *, user_id: int, query: str) -> list[MedicalRecord]:
        normalized = f"%{query.strip().lower()}%"
        statement = (
            select(MedicalRecord)
            .options(
                selectinload(MedicalRecord.documents),
                selectinload(MedicalRecord.schedules),
                selectinload(MedicalRecord.inventory_items),
                selectinload(MedicalRecord.medicines),
            )
            .where(
                MedicalRecord.user_id == user_id,
                MedicalRecord.is_deleted.is_(False),
                or_(
                    MedicalRecord.title.ilike(normalized),
                    MedicalRecord.folder_name.ilike(normalized),
                    MedicalRecord.hospital_name.ilike(normalized),
                    MedicalRecord.doctor_name.ilike(normalized),
                    MedicalRecord.diagnosis.ilike(normalized),
                ),
            )
            .order_by(MedicalRecord.created_at.desc(), MedicalRecord.id.desc())
        )
        return list(self.session.execute(statement).scalars().unique().all())

    def filter_records(
        self,
        *,
        user_id: int,
        document_type: str | None = None,
        hospital: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[MedicalRecord]:
        statement = (
            select(MedicalRecord)
            .options(
                selectinload(MedicalRecord.documents),
                selectinload(MedicalRecord.schedules),
                selectinload(MedicalRecord.inventory_items),
                selectinload(MedicalRecord.medicines),
            )
            .where(
                MedicalRecord.user_id == user_id,
                MedicalRecord.is_deleted.is_(False),
            )
        )
        if hospital:
            statement = statement.where(MedicalRecord.hospital_name.ilike(f"%{hospital.strip()}%"))
        if date_from:
            statement = statement.where(MedicalRecord.visit_date.is_not(None), MedicalRecord.visit_date >= date_from)
        if date_to:
            statement = statement.where(MedicalRecord.visit_date.is_not(None), MedicalRecord.visit_date <= date_to)
        statement = statement.order_by(MedicalRecord.created_at.desc(), MedicalRecord.id.desc())
        records = list(self.session.execute(statement).scalars().unique().all())
        if document_type:
            records = [
                record
                for record in records
                if any((not document.is_deleted) and document.document_type == document_type for document in record.documents)
            ]
        return records

    def link_schedule(self, record: MedicalRecord, schedule: Schedule) -> MedicalRecord:
        if schedule not in record.schedules:
            record.schedules.append(schedule)
            self.session.add(record)
            self.session.commit()
            self.session.refresh(record)
        return record

    def link_inventory(self, record: MedicalRecord, inventory_item: InventoryItem) -> MedicalRecord:
        if inventory_item not in record.inventory_items:
            record.inventory_items.append(inventory_item)
            self.session.add(record)
            self.session.commit()
            self.session.refresh(record)
        return record

    def link_medicine(self, record: MedicalRecord, medicine: Medicine) -> MedicalRecord:
        if medicine not in record.medicines:
            record.medicines.append(medicine)
            self.session.add(record)
            self.session.commit()
            self.session.refresh(record)
        return record

    def get_document_by_storage_path(self, *, record_id: int, storage_path: str) -> MedicalRecordDocument | None:
        statement = select(MedicalRecordDocument).where(
            MedicalRecordDocument.medical_record_id == record_id,
            MedicalRecordDocument.storage_path == storage_path,
            MedicalRecordDocument.is_deleted.is_(False),
        )
        return self.session.execute(statement).scalar_one_or_none()
