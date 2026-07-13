from datetime import date

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import joinedload, selectinload

from app.core.enums import ScheduleStatus
from app.models.schedule import Schedule
from app.models.schedule_reminder import ScheduleReminder
from app.repositories.base import BaseRepository
from app.utils.datetime import utc_now


class ScheduleRepository(BaseRepository):
    def create_schedule(self, schedule: Schedule, reminders: list[ScheduleReminder]) -> Schedule:
        self.session.add(schedule)
        self.session.flush()
        for reminder in reminders:
            reminder.schedule_id = schedule.id
            self.session.add(reminder)
        self.session.commit()
        self.session.refresh(schedule)
        return schedule

    def update_schedule(self, schedule: Schedule, reminders: list[ScheduleReminder] | None = None) -> Schedule:
        self.session.add(schedule)
        if reminders is not None:
            for existing in schedule.reminders:
                existing.is_deleted = True
                existing.deleted_at = utc_now()
                self.session.add(existing)
            for reminder in reminders:
                reminder.schedule_id = schedule.id
                self.session.add(reminder)
        self.session.commit()
        self.session.refresh(schedule)
        return schedule

    def delete_schedule(self, schedule: Schedule) -> None:
        schedule.is_deleted = True
        schedule.deleted_at = utc_now()
        self.session.add(schedule)
        for reminder in schedule.reminders:
            reminder.is_deleted = True
            reminder.deleted_at = utc_now()
            self.session.add(reminder)
        self.session.commit()

    def get_schedule_by_id(self, *, user_id: int, schedule_id: int) -> Schedule | None:
        statement = (
            select(Schedule)
            .options(joinedload(Schedule.medicine), selectinload(Schedule.reminders))
            .where(
                Schedule.id == schedule_id,
                Schedule.user_id == user_id,
                Schedule.is_deleted.is_(False),
            )
        )
        return self.session.execute(statement).scalars().unique().one_or_none()

    def get_schedules_by_user(self, *, user_id: int) -> list[Schedule]:
        statement = (
            select(Schedule)
            .options(joinedload(Schedule.medicine), selectinload(Schedule.reminders))
            .where(
                Schedule.user_id == user_id,
                Schedule.is_deleted.is_(False),
            )
            .order_by(Schedule.start_date.desc(), Schedule.id.desc())
        )
        return list(self.session.execute(statement).scalars().unique().all())

    def get_schedules_by_date(self, *, user_id: int, target_date: date) -> list[Schedule]:
        statement = (
            select(Schedule)
            .join(Schedule.reminders)
            .options(joinedload(Schedule.medicine), selectinload(Schedule.reminders))
            .where(
                Schedule.user_id == user_id,
                Schedule.is_deleted.is_(False),
                ScheduleReminder.is_deleted.is_(False),
                ScheduleReminder.reminder_date == target_date,
            )
            .order_by(ScheduleReminder.reminder_time.asc(), Schedule.id.asc())
        )
        return list(self.session.execute(statement).scalars().unique().all())

    def get_todays_schedule(self, *, user_id: int, today: date) -> list[Schedule]:
        return self.get_schedules_by_date(user_id=user_id, target_date=today)

    def get_active_schedules(self, *, user_id: int) -> list[Schedule]:
        statement = (
            select(Schedule)
            .options(joinedload(Schedule.medicine), selectinload(Schedule.reminders))
            .where(
                Schedule.user_id == user_id,
                Schedule.is_deleted.is_(False),
                Schedule.status == ScheduleStatus.ACTIVE,
            )
            .order_by(Schedule.start_date.asc(), Schedule.id.asc())
        )
        return list(self.session.execute(statement).scalars().unique().all())

    def get_duplicate_active_schedule(
        self,
        *,
        user_id: int,
        medicine_id: int,
        start_date: date,
        end_date: date,
        exclude_schedule_id: int | None = None,
    ) -> Schedule | None:
        statement = select(Schedule).where(
            Schedule.user_id == user_id,
            Schedule.medicine_id == medicine_id,
            Schedule.is_deleted.is_(False),
            Schedule.status == ScheduleStatus.ACTIVE,
            or_(
                and_(Schedule.start_date <= start_date, or_(Schedule.end_date.is_(None), Schedule.end_date >= start_date)),
                and_(Schedule.start_date <= end_date, or_(Schedule.end_date.is_(None), Schedule.end_date >= end_date)),
                and_(Schedule.start_date >= start_date, Schedule.start_date <= end_date),
            ),
        )
        if exclude_schedule_id is not None:
            statement = statement.where(Schedule.id != exclude_schedule_id)
        return self.session.execute(statement).scalar_one_or_none()

    def get_reminder_by_id(self, *, user_id: int, reminder_id: int) -> ScheduleReminder | None:
        statement = (
            select(ScheduleReminder)
            .join(ScheduleReminder.schedule)
            .where(
                ScheduleReminder.id == reminder_id,
                ScheduleReminder.is_deleted.is_(False),
                Schedule.user_id == user_id,
                Schedule.is_deleted.is_(False),
            )
        )
        return self.session.execute(statement).scalar_one_or_none()

    def mark_reminder_completed(self, reminder: ScheduleReminder) -> ScheduleReminder:
        reminder.completed_at = utc_now()
        self.session.add(reminder)
        self.session.commit()
        self.session.refresh(reminder)
        return reminder
