from datetime import date, time

from sqlalchemy import Date, Enum as SqlEnum, Float, ForeignKey, Index, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import FoodTiming, ScheduleSource, ScheduleStatus
from app.db.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin


class Schedule(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "schedules"
    __table_args__ = (
        Index("ix_schedules_user_status", "user_id", "status"),
        Index("ix_schedules_user_start_date", "user_id", "start_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    medicine_id: Mapped[int] = mapped_column(ForeignKey("medicines.id"), nullable=False)
    dosage_amount: Mapped[str | None] = mapped_column(String(50), nullable=True)
    dosage_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    dosage_pattern: Mapped[str | None] = mapped_column(String(50), nullable=True)
    food_timing: Mapped[FoodTiming | None] = mapped_column(
        SqlEnum(
            FoodTiming,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            native_enum=False,
        ),
        nullable=True,
    )
    frequency: Mapped[str | None] = mapped_column(String(100), nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    reminder_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    pharmacy_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[ScheduleStatus] = mapped_column(
        SqlEnum(
            ScheduleStatus,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            native_enum=False,
        ),
        default=ScheduleStatus.ACTIVE,
        nullable=False,
    )
    source: Mapped[ScheduleSource] = mapped_column(
        SqlEnum(
            ScheduleSource,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            native_enum=False,
        ),
        default=ScheduleSource.PHARMACY_BILL,
        nullable=False,
    )

    user = relationship("User", back_populates="schedules")
    medicine = relationship("Medicine", back_populates="schedules")
    notifications = relationship("Notification", back_populates="schedule")
    reminders = relationship("ScheduleReminder", back_populates="schedule")
    medical_records = relationship(
        "MedicalRecord",
        secondary="medical_record_schedules",
        back_populates="schedules",
    )
