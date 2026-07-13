from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, Enum as SqlEnum, ForeignKey, Index, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ReminderPeriod
from app.db.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin


class ScheduleReminder(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "schedule_reminders"
    __table_args__ = (
        Index("ix_schedule_reminders_schedule_date", "schedule_id", "reminder_date"),
        Index("ix_schedule_reminders_date_time", "reminder_date", "reminder_time"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.id"), nullable=False)
    reminder_date: Mapped[date] = mapped_column(Date, nullable=False)
    reminder_time: Mapped[time] = mapped_column(Time, nullable=False)
    period: Mapped[ReminderPeriod] = mapped_column(
        SqlEnum(
            ReminderPeriod,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            native_enum=False,
        ),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    schedule = relationship("Schedule", back_populates="reminders")
