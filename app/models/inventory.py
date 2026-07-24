from datetime import date

from sqlalchemy import Date, Enum as SqlEnum, Float, ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import InventoryStatus
from app.db.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin


class InventoryItem(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "inventory"
    __table_args__ = (
        Index("ix_inventory_user_status", "user_id", "status"),
        Index("ix_inventory_expiry_date", "expiry_date"),
        # Database-level protection against duplicate inventory rows for the same
        # user, medicine, and expiry date. Implemented as a *partial* unique index
        # so it only applies to non-deleted rows -- soft-deleted history does not
        # block future inserts. PostgreSQL and SQLite both support partial unique
        # indexes; the ``sqlite_where``/``postgresql_where`` clauses provide the
        # dialect-specific predicate. This mirrors the constraint created by
        # Alembic migration ``20260724_0004`` so that ``Base.metadata.create_all``
        # and the migration-managed schema stay in sync.
        Index(
            "uq_inventory_user_medicine_expiry_active",
            "user_id",
            "medicine_id",
            "expiry_date",
            unique=True,
            sqlite_where=text("is_deleted = 0"),
            postgresql_where=text("is_deleted = false"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    medicine_id: Mapped[int] = mapped_column(ForeignKey("medicines.id"), nullable=False)
    quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    quantity_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[InventoryStatus] = mapped_column(
        SqlEnum(
            InventoryStatus,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            native_enum=False,
        ),
        default=InventoryStatus.AVAILABLE,
        nullable=False,
        index=True,
    )
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="inventory_items")
    medicine = relationship("Medicine", back_populates="inventory_items")
    medical_records = relationship(
        "MedicalRecord",
        secondary="medical_record_inventory_items",
        back_populates="inventory_items",
    )