from datetime import date, time

from sqlalchemy.orm import Session

from app.auth.password import hash_password
from app.core.enums import (
    InventoryStatus,
    MedicineType,
    NotificationStatus,
    NotificationType,
    ScheduleSource,
    ScheduleStatus,
)
from app.models.inventory import InventoryItem
from app.models.medical_record import MedicalRecord, MedicalRecordDocument
from app.models.medicine import Medicine
from app.models.notification import Notification
from app.models.schedule import Schedule
from app.models.user import User


def create_user(
    session: Session,
    *,
    full_name: str = "Dashboard User",
    email: str = "dashboard@example.com",
    password: str = "Password123",
) -> User:
    user = User(
        full_name=full_name,
        email=email,
        password_hash=hash_password(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_medicine(
    session: Session,
    *,
    name: str = "Paracetamol 500",
    generic_name: str = "Paracetamol",
    brand_name: str | None = None,
    composition: str | None = None,
    strength: str | None = "500",
    unit: str | None = "mg",
    dosage_form: MedicineType = MedicineType.TABLET,
    route: str | None = "oral",
) -> Medicine:
    medicine = Medicine(
        name=name,
        generic_name=generic_name,
        brand_name=brand_name,
        composition=composition or generic_name,
        strength=strength,
        unit=unit,
        dosage_form=dosage_form,
        route=route,
    )
    session.add(medicine)
    session.commit()
    session.refresh(medicine)
    return medicine


def create_schedule(
    session: Session,
    *,
    user_id: int,
    medicine_id: int,
    start_date: date,
    end_date: date | None = None,
    reminder_time: time | None = None,
    dosage_amount: str = "1",
    dosage_unit: str = "tablet",
    frequency: str = "Once daily",
    status: ScheduleStatus = ScheduleStatus.ACTIVE,
) -> Schedule:
    schedule = Schedule(
        user_id=user_id,
        medicine_id=medicine_id,
        start_date=start_date,
        end_date=end_date,
        reminder_time=reminder_time,
        dosage_amount=dosage_amount,
        dosage_unit=dosage_unit,
        frequency=frequency,
        status=status,
        source=ScheduleSource.PHARMACY_BILL,
    )
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    return schedule


def create_inventory_item(
    session: Session,
    *,
    user_id: int,
    medicine_id: int,
    status: InventoryStatus = InventoryStatus.AVAILABLE,
    quantity: float | None = None,
    quantity_unit: str | None = None,
    expiry_date=None,
    purchase_date=None,
) -> InventoryItem:
    inventory_item = InventoryItem(
        user_id=user_id,
        medicine_id=medicine_id,
        quantity=quantity,
        quantity_unit=quantity_unit,
        status=status,
        expiry_date=expiry_date,
        purchase_date=purchase_date,
    )
    session.add(inventory_item)
    session.commit()
    session.refresh(inventory_item)
    return inventory_item


def create_notification(
    session: Session,
    *,
    user_id: int,
    title: str = "Reminder",
    body: str = "Take medicine",
    status: NotificationStatus = NotificationStatus.PENDING,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        notification_type=NotificationType.REMINDER,
        status=status,
        title=title,
        body=body,
    )
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification


def create_medical_record(
    session: Session,
    *,
    user_id: int,
    title: str = "Cardiology Visit",
    folder_name: str = "Cardiology",
    hospital_name: str | None = "City Hospital",
    doctor_name: str | None = "Dr. Sharma",
    visit_date: date | None = None,
    diagnosis: str | None = "Hypertension",
    treatment_name: str | None = "Medication Review",
    notes: str | None = "Follow-up in two weeks",
    description: str | None = "Initial consultation",
    linked_generic_search_ids: list[str] | None = None,
) -> MedicalRecord:
    record = MedicalRecord(
        user_id=user_id,
        title=title,
        folder_name=folder_name,
        hospital_name=hospital_name,
        doctor_name=doctor_name,
        visit_date=visit_date,
        diagnosis=diagnosis,
        treatment_name=treatment_name,
        notes=notes,
        description=description,
        linked_generic_search_ids=linked_generic_search_ids or [],
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def create_medical_record_document(
    session: Session,
    *,
    medical_record_id: int,
    document_type,
    file_name: str = "prescription.pdf",
    file_type: str = "application/pdf",
    file_size: int = 2048,
    storage_path: str = "/records/prescription.pdf",
    consultation_date: date | None = None,
    diagnosis: str | None = "Hypertension",
) -> MedicalRecordDocument:
    document = MedicalRecordDocument(
        medical_record_id=medical_record_id,
        document_type=document_type,
        file_name=file_name,
        file_path=storage_path,
        storage_path=storage_path,
        file_type=file_type,
        file_size=file_size,
        mime_type=file_type,
        consultation_date=consultation_date,
        diagnosis=diagnosis,
    )
    session.add(document)
    session.commit()
    session.refresh(document)
    return document
