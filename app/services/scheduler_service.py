from datetime import date, datetime, time, timedelta

from app.core.enums import ReminderPeriod, ScheduleSource, ScheduleStatus
from app.core.exceptions import AppException
from app.models.schedule import Schedule
from app.models.schedule_reminder import ScheduleReminder
from app.repositories.medicine_repository import MedicineRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.schemas.schedule import (
    BillMedicineInput,
    ScheduleCompleteRequest,
    ScheduleCreateRequest,
    ScheduleDeleteResponse,
    ScheduleListResponse,
    ScheduleReminderResponse,
    ScheduleResponse,
    ScheduleUpdateRequest,
)
from app.services.inventory_integration_service import InventoryIntegrationService


DEFAULT_REMINDER_TIMES = {
    ReminderPeriod.MORNING: time(8, 0),
    ReminderPeriod.AFTERNOON: time(14, 0),
    ReminderPeriod.NIGHT: time(20, 0),
}


class SchedulerService:
    def __init__(self, session) -> None:
        self.session = session
        self.schedule_repository = ScheduleRepository(session)
        self.medicine_repository = MedicineRepository(session)
        self.inventory_integration_service = InventoryIntegrationService(session)

    def list_schedules(self, *, user_id: int) -> ScheduleListResponse:
        schedules = self.schedule_repository.get_schedules_by_user(user_id=user_id)
        return ScheduleListResponse(items=[self._to_response(schedule) for schedule in schedules])

    def get_schedule(self, *, user_id: int, schedule_id: int) -> ScheduleResponse:
        schedule = self.schedule_repository.get_schedule_by_id(user_id=user_id, schedule_id=schedule_id)
        if schedule is None:
            raise AppException("Schedule not found.", 404, "schedule_not_found")
        return self._to_response(schedule)

    def create_schedule(self, *, user_id: int, payload: ScheduleCreateRequest) -> ScheduleResponse:
        medicine = self._get_medicine_or_raise(payload.medicine_id)
        end_date = self._resolve_end_date(start_date=payload.start_date, end_date=payload.end_date, duration_days=payload.duration_days)
        self._validate_schedule_dates(
            start_date=payload.start_date,
            end_date=end_date,
            expiry_date=payload.expiry_date,
            purchase_date=payload.purchase_date,
        )
        self._ensure_no_duplicate_schedule(user_id=user_id, medicine_id=medicine.id, start_date=payload.start_date, end_date=end_date)

        reminders = self._build_reminders(
            dosage_pattern=payload.dosage_pattern,
            start_date=payload.start_date,
            end_date=end_date,
            reminder_times=payload.reminder_times,
        )
        schedule = Schedule(
            user_id=user_id,
            medicine_id=medicine.id,
            dosage_amount=payload.dosage_pattern,
            dosage_unit=payload.quantity_unit,
            dosage_pattern=payload.dosage_pattern,
            food_timing=payload.food_timing,
            frequency="daily",
            instructions=payload.food_timing.value,
            notes=payload.notes,
            duration_days=payload.duration_days,
            start_date=payload.start_date,
            end_date=end_date,
            purchase_date=payload.purchase_date,
            expiry_date=payload.expiry_date,
            quantity=payload.quantity,
            reminder_time=min(reminder.reminder_time for reminder in reminders),
            pharmacy_name=payload.pharmacy_name,
            status=ScheduleStatus.ACTIVE,
            source=payload.source,
        )

        with self._transaction_scope():
            created = self.schedule_repository.create_schedule(schedule, reminders, commit=False)
            self._integrate_inventory(
                user_id=user_id,
                medicine_id=medicine.id,
                quantity=payload.quantity,
                quantity_unit=payload.quantity_unit,
                expiry_date=payload.expiry_date,
                commit=False,
            )
        created = self.schedule_repository.get_schedule_by_id(user_id=user_id, schedule_id=created.id)
        return self._to_response(created)

    def update_schedule(self, *, user_id: int, schedule_id: int, payload: ScheduleUpdateRequest) -> ScheduleResponse:
        schedule = self.schedule_repository.get_schedule_by_id(user_id=user_id, schedule_id=schedule_id)
        if schedule is None:
            raise AppException("Schedule not found.", 404, "schedule_not_found")

        dosage_pattern = payload.dosage_pattern or schedule.dosage_pattern or schedule.dosage_amount or "1-0-0"
        start_date = payload.start_date or schedule.start_date
        end_date = self._resolve_end_date(
            start_date=start_date,
            end_date=payload.end_date or schedule.end_date,
            duration_days=payload.duration_days if payload.duration_days is not None else schedule.duration_days,
        )
        expiry_date = payload.expiry_date if payload.expiry_date is not None else schedule.expiry_date
        purchase_date = payload.purchase_date if payload.purchase_date is not None else schedule.purchase_date
        self._validate_schedule_dates(
            start_date=start_date,
            end_date=end_date,
            expiry_date=expiry_date,
            purchase_date=purchase_date,
        )
        self._ensure_no_duplicate_schedule(
            user_id=user_id,
            medicine_id=schedule.medicine_id,
            start_date=start_date,
            end_date=end_date,
            exclude_schedule_id=schedule.id,
        )

        reminders = self._build_reminders(
            dosage_pattern=dosage_pattern,
            start_date=start_date,
            end_date=end_date,
            reminder_times=payload.reminder_times,
        )

        schedule.dosage_amount = dosage_pattern
        schedule.dosage_unit = payload.quantity_unit if payload.quantity_unit is not None else schedule.dosage_unit
        schedule.dosage_pattern = dosage_pattern
        schedule.food_timing = payload.food_timing or schedule.food_timing
        schedule.instructions = (payload.food_timing or schedule.food_timing).value if (payload.food_timing or schedule.food_timing) else schedule.instructions
        schedule.notes = payload.notes if payload.notes is not None else schedule.notes
        schedule.duration_days = payload.duration_days if payload.duration_days is not None else schedule.duration_days
        schedule.start_date = start_date
        schedule.end_date = end_date
        schedule.purchase_date = purchase_date
        schedule.expiry_date = expiry_date
        schedule.quantity = payload.quantity if payload.quantity is not None else schedule.quantity
        schedule.reminder_time = min(reminder.reminder_time for reminder in reminders)
        schedule.pharmacy_name = payload.pharmacy_name if payload.pharmacy_name is not None else schedule.pharmacy_name
        schedule.status = payload.status or schedule.status

        updated = self.schedule_repository.update_schedule(schedule, reminders)
        updated = self.schedule_repository.get_schedule_by_id(user_id=user_id, schedule_id=updated.id)
        return self._to_response(updated)

    def delete_schedule(self, *, user_id: int, schedule_id: int) -> ScheduleDeleteResponse:
        schedule = self.schedule_repository.get_schedule_by_id(user_id=user_id, schedule_id=schedule_id)
        if schedule is None:
            raise AppException("Schedule not found.", 404, "schedule_not_found")
        self.schedule_repository.delete_schedule(schedule)
        return ScheduleDeleteResponse(message="Schedule deleted successfully.")

    def get_todays_schedule(self, *, user_id: int, today: date | None = None) -> ScheduleListResponse:
        target_date = today or date.today()
        schedules = self.schedule_repository.get_todays_schedule(user_id=user_id, today=target_date)
        return ScheduleListResponse(
            items=[self._to_response(schedule, reminder_date_filter=target_date) for schedule in schedules]
        )

    def create_schedule_from_bill(self, *, user_id: int, payload: BillMedicineInput) -> ScheduleResponse:
        medicines = self.medicine_repository.search_branded_medicine(payload.medicine_name)
        if not medicines:
            raise AppException("Unknown medicine.", 404, "unknown_medicine")
        if len(medicines) > 1:
            raise AppException("Duplicate medicine definitions found.", 409, "duplicate_medicine")
        request = ScheduleCreateRequest(
            medicine_id=medicines[0].id,
            dosage_pattern=payload.dosage_pattern,
            food_timing=payload.food_timing,
            start_date=payload.start_date,
            end_date=payload.end_date,
            duration_days=payload.duration_days,
            reminder_times=payload.reminder_times,
            notes=payload.notes,
            quantity=payload.quantity,
            purchase_date=payload.purchase_date,
            expiry_date=payload.expiry_date,
            pharmacy_name=payload.pharmacy_name,
            source=ScheduleSource.PHARMACY_BILL,
        )
        return self.create_schedule(user_id=user_id, payload=request)

    def complete_reminder(self, *, user_id: int, payload: ScheduleCompleteRequest) -> ScheduleReminderResponse:
        reminder = self.schedule_repository.get_reminder_by_id(user_id=user_id, reminder_id=payload.reminder_id)
        if reminder is None:
            raise AppException("Reminder not found.", 404, "reminder_not_found")
        schedule = reminder.schedule
        dosage_pattern = schedule.dosage_pattern or schedule.dosage_amount or "0-0-0"
        with self._transaction_scope():
            self._consume_inventory_for_completion(
                user_id=user_id,
                medicine_id=schedule.medicine_id,
                dosage_pattern=dosage_pattern,
                period=reminder.period,
                commit=False,
            )
            completed = self.schedule_repository.mark_reminder_completed(reminder, commit=False)
        return self._to_reminder_response(completed)

    def _resolve_end_date(self, *, start_date: date, end_date: date | None, duration_days: int | None) -> date:
        if end_date is not None:
            return end_date
        if duration_days is not None:
            if duration_days <= 0:
                raise AppException("Negative duration is not allowed.", 422, "invalid_duration")
            return start_date + timedelta(days=duration_days - 1)
        return start_date

    def _validate_schedule_dates(
        self,
        *,
        start_date: date,
        end_date: date,
        expiry_date: date | None,
        purchase_date: date | None,
    ) -> None:
        if end_date < start_date:
            raise AppException("Invalid dates.", 422, "invalid_dates")
        if purchase_date and expiry_date and expiry_date < purchase_date:
            raise AppException("Invalid dates.", 422, "invalid_dates")
        if expiry_date and expiry_date < start_date:
            raise AppException("Expired medicine cannot be scheduled.", 422, "expired_medicine")

    def _build_reminders(self, *, dosage_pattern: str, start_date: date, end_date: date, reminder_times) -> list[ScheduleReminder]:
        morning, afternoon, night = [int(part) for part in dosage_pattern.split("-")]
        period_map = [
            (ReminderPeriod.MORNING, morning),
            (ReminderPeriod.AFTERNOON, afternoon),
            (ReminderPeriod.NIGHT, night),
        ]
        reminder_times = reminder_times or {}
        reminders: list[ScheduleReminder] = []
        current_date = start_date
        while current_date <= end_date:
            for period, dosage_count in period_map:
                if dosage_count <= 0:
                    continue
                period_time = getattr(reminder_times, period.value, None) if hasattr(reminder_times, period.value) else None
                reminder_time = period_time or DEFAULT_REMINDER_TIMES[period]
                reminders.append(
                    ScheduleReminder(
                        reminder_date=current_date,
                        reminder_time=reminder_time,
                        period=period,
                    )
                )
            current_date += timedelta(days=1)
        if not reminders:
            raise AppException("Invalid dosage.", 422, "invalid_dosage")
        return reminders

    def _ensure_no_duplicate_schedule(
        self,
        *,
        user_id: int,
        medicine_id: int,
        start_date: date,
        end_date: date,
        exclude_schedule_id: int | None = None,
    ) -> None:
        duplicate = self.schedule_repository.get_duplicate_active_schedule(
            user_id=user_id,
            medicine_id=medicine_id,
            start_date=start_date,
            end_date=end_date,
            exclude_schedule_id=exclude_schedule_id,
        )
        if duplicate is not None:
            raise AppException("Duplicate active schedule.", 409, "duplicate_active_schedule")

    def _integrate_inventory(
        self,
        *,
        user_id: int,
        medicine_id: int,
        quantity: float | None,
        quantity_unit: str | None,
        expiry_date: date | None,
        commit: bool = True,
    ) -> None:
        try:
            self.inventory_integration_service.add_scheduler_medicine(
                user_id=user_id,
                medicine_id=medicine_id,
                quantity=quantity,
                quantity_unit=quantity_unit,
                expiry_date=expiry_date,
                commit=commit,
            )
        except AppException as exc:
            raise AppException(
                f"Inventory integration failure: {exc.message}",
                exc.status_code,
                "inventory_integration_failure",
            ) from exc

    def _consume_inventory_for_completion(
        self,
        *,
        user_id: int,
        medicine_id: int,
        dosage_pattern: str,
        period: ReminderPeriod,
        commit: bool = True,
    ) -> None:
        try:
            self.inventory_integration_service.consume_scheduler_medicine(
                user_id=user_id,
                medicine_id=medicine_id,
                dosage_pattern=dosage_pattern,
                period=period,
                commit=commit,
            )
        except AppException as exc:
            raise AppException(
                f"Inventory integration failure: {exc.message}",
                exc.status_code,
                "inventory_integration_failure",
            ) from exc

    def _transaction_scope(self):
        if self.session.in_transaction():
            return self.session.begin_nested()
        return self.session.begin()

    def _get_medicine_or_raise(self, medicine_id: int):
        medicine = self.medicine_repository.get_medicine_by_id(medicine_id)
        if medicine is None:
            raise AppException("Unknown medicine.", 404, "unknown_medicine")
        return medicine

    def _to_response(self, schedule: Schedule, reminder_date_filter: date | None = None) -> ScheduleResponse:
        reminders = [
            reminder
            for reminder in schedule.reminders
            if not reminder.is_deleted
            and (reminder_date_filter is None or reminder.reminder_date == reminder_date_filter)
        ]
        return ScheduleResponse(
            id=schedule.id,
            medicine_id=schedule.medicine_id,
            medicine_name=schedule.medicine.name,
            dosage_pattern=schedule.dosage_pattern or schedule.dosage_amount or "",
            food_timing=schedule.food_timing,
            start_date=schedule.start_date,
            end_date=schedule.end_date,
            duration_days=schedule.duration_days,
            quantity=schedule.quantity,
            quantity_unit=schedule.dosage_unit,
            purchase_date=schedule.purchase_date,
            expiry_date=schedule.expiry_date,
            pharmacy_name=schedule.pharmacy_name,
            notes=schedule.notes,
            status=schedule.status,
            source=schedule.source,
            reminder_time=schedule.reminder_time,
            reminders=[
                self._to_reminder_response(reminder)
                for reminder in sorted(reminders, key=lambda item: (item.reminder_date, item.reminder_time))
            ],
        )

    def _to_reminder_response(self, reminder: ScheduleReminder) -> ScheduleReminderResponse:
        return ScheduleReminderResponse(
            id=reminder.id,
            reminder_date=reminder.reminder_date,
            reminder_time=reminder.reminder_time,
            period=reminder.period,
            completed_at=reminder.completed_at,
        )
