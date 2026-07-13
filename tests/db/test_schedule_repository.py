from datetime import date, time, timedelta

from app.core.enums import ReminderPeriod, ScheduleSource, ScheduleStatus
from app.models.schedule import Schedule
from app.models.schedule_reminder import ScheduleReminder
from app.repositories.schedule_repository import ScheduleRepository
from tests.support import create_medicine, create_user


def test_schedule_repository_supports_create_lookup_date_and_completion(db_session):
    user = create_user(db_session, email="schedule-repo@example.com")
    medicine = create_medicine(db_session, name="Schedule Med")
    schedule = Schedule(
        user_id=user.id,
        medicine_id=medicine.id,
        dosage_amount="1-0-1",
        dosage_pattern="1-0-1",
        frequency="daily",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=1),
        reminder_time=time(8, 0),
        status=ScheduleStatus.ACTIVE,
        source=ScheduleSource.MANUAL,
    )
    reminders = [
        ScheduleReminder(
            reminder_date=date.today(),
            reminder_time=time(8, 0),
            period=ReminderPeriod.MORNING,
        ),
        ScheduleReminder(
            reminder_date=date.today(),
            reminder_time=time(20, 0),
            period=ReminderPeriod.NIGHT,
        ),
    ]
    repository = ScheduleRepository(db_session)

    created = repository.create_schedule(schedule, reminders)
    fetched = repository.get_schedule_by_id(user_id=user.id, schedule_id=created.id)
    today_items = repository.get_todays_schedule(user_id=user.id, today=date.today())
    active = repository.get_active_schedules(user_id=user.id)
    by_date = repository.get_schedules_by_date(user_id=user.id, target_date=date.today())
    reminder = repository.get_reminder_by_id(user_id=user.id, reminder_id=fetched.reminders[0].id)
    completed = repository.mark_reminder_completed(reminder)

    assert fetched is not None
    assert len(fetched.reminders) == 2
    assert len(today_items) == 1
    assert len(active) == 1
    assert len(by_date) == 1
    assert completed.completed_at is not None

