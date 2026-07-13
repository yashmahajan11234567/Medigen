from sqlalchemy import Enum as SqlEnum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import MedicineType
from app.db.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin


class Medicine(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "medicines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    generic_name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    brand_name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    composition: Mapped[str | None] = mapped_column(Text, nullable=True)
    strength: Mapped[str | None] = mapped_column(String(100), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    dosage_form: Mapped[MedicineType] = mapped_column(
        SqlEnum(
            MedicineType,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            native_enum=False,
        ),
        default=MedicineType.OTHER,
        nullable=False,
    )
    route: Mapped[str | None] = mapped_column(String(50), nullable=True)

    inventory_items = relationship("InventoryItem", back_populates="medicine")
    schedules = relationship("Schedule", back_populates="medicine")
    medical_records = relationship(
        "MedicalRecord",
        secondary="medical_record_medicines",
        back_populates="medicines",
    )
