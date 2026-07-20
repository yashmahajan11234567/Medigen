from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Column,
    Date,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import MedicalRecordDocumentType
from app.db.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin
from app.utils.datetime import utc_now


medical_record_schedules = Table(
    "medical_record_schedules",
    Base.metadata,
    Column("medical_record_id", ForeignKey("medical_records.id"), primary_key=True),
    Column("schedule_id", ForeignKey("schedules.id"), primary_key=True),
)


medical_record_inventory_items = Table(
    "medical_record_inventory_items",
    Base.metadata,
    Column("medical_record_id", ForeignKey("medical_records.id"), primary_key=True),
    Column("inventory_item_id", ForeignKey("inventory.id"), primary_key=True),
)


medical_record_medicines = Table(
    "medical_record_medicines",
    Base.metadata,
    Column("medical_record_id", ForeignKey("medical_records.id"), primary_key=True),
    Column("medicine_id", ForeignKey("medicines.id"), primary_key=True),
)


class MedicalRecord(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "medical_records"
    __table_args__ = (
        Index("ix_medical_records_user_title", "user_id", "title"),
        Index("ix_medical_records_folder_name", "folder_name"),
        Index("ix_medical_records_visit_date", "visit_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    folder_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    hospital_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    doctor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    visit_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    diagnosis: Mapped[str | None] = mapped_column(String(255), nullable=True)
    treatment_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    linked_generic_search_ids: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    user = relationship("User", back_populates="medical_records")
    documents = relationship("MedicalRecordDocument", back_populates="medical_record")
    schedules = relationship(
        "Schedule",
        secondary=medical_record_schedules,
        back_populates="medical_records",
    )
    inventory_items = relationship(
        "InventoryItem",
        secondary=medical_record_inventory_items,
        back_populates="medical_records",
    )
    medicines = relationship(
        "Medicine",
        secondary=medical_record_medicines,
        back_populates="medical_records",
    )


class MedicalRecordDocument(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "medical_record_documents"
    __table_args__ = (
        UniqueConstraint("medical_record_id", "storage_path", name="uq_record_document_storage_path"),
        Index("ix_medical_record_documents_record_type", "medical_record_id", "document_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    medical_record_id: Mapped[int] = mapped_column(ForeignKey("medical_records.id"), nullable=False)
    document_type: Mapped[MedicalRecordDocumentType] = mapped_column(
        SqlEnum(
            MedicalRecordDocumentType,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            native_enum=False,
        ),
        nullable=False,
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    upload_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    mime_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    doctor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hospital_or_clinic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    doctor_specialty: Mapped[str | None] = mapped_column(String(255), nullable=True)
    consultation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    follow_up_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    diagnosis: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_confidence: Mapped[float | None] = mapped_column(nullable=True)
    ocr_processed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ocr_source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    blur_score: Mapped[float | None] = mapped_column(nullable=True)
    brightness: Mapped[float | None] = mapped_column(nullable=True)
    contrast: Mapped[float | None] = mapped_column(nullable=True)
    is_pass: Mapped[bool | None] = mapped_column(nullable=True)
    issues: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    medical_record = relationship("MedicalRecord", back_populates="documents")
