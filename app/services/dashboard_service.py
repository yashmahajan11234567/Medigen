from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppException
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import (
    DashboardInventorySummary,
    DashboardResponse,
    DashboardScheduleItem,
    DashboardUserSummary,
)
from app.services.inventory_service import InventoryService


class DashboardService:
    def __init__(self, session) -> None:
        self.repository = DashboardRepository(session)
        self.inventory_service = InventoryService(session)

    def get_dashboard(self, user_id: int, current_datetime: datetime | None = None) -> DashboardResponse:
        now = current_datetime or datetime.now()

        try:
            user = self.repository.get_user_by_id(user_id)
            if user is None:
                raise AppException(
                    message="Dashboard user was not found.",
                    status_code=404,
                    code="dashboard_user_not_found",
                )

            notification_count = self.repository.get_unread_notification_count(user_id)
            today_schedule = self.repository.get_todays_schedule(user_id, now.date())
            inventory_summary = self.inventory_service.get_inventory_summary(user_id=user_id)
        except AppException:
            raise
        except SQLAlchemyError as exc:
            raise AppException(
                message="A database error occurred while loading the dashboard.",
                status_code=500,
                code="database_error",
            ) from exc

        return DashboardResponse(
            user=DashboardUserSummary(id=user.id, name=user.full_name),
            greeting=self.get_greeting(now),
            notification_count=notification_count,
            today_schedule=[
                DashboardScheduleItem(
                    id=schedule.id,
                    medicine_id=schedule.medicine_id,
                    medicine_name=schedule.medicine.name,
                    dosage_amount=schedule.dosage_amount,
                    dosage_unit=schedule.dosage_unit,
                    frequency=schedule.frequency,
                    reminder_time=schedule.reminder_time,
                )
                for schedule in today_schedule
            ],
            inventory_summary=DashboardInventorySummary(
                total_medicines=inventory_summary.total_medicines,
                expiring_soon=inventory_summary.expiring_soon,
            ),
        )

    def get_greeting(self, current_datetime: datetime | None = None) -> str:
        hour = (current_datetime or datetime.now()).hour

        if 5 <= hour < 12:
            return "Good Morning"
        if 12 <= hour < 17:
            return "Good Afternoon"
        if 17 <= hour < 21:
            return "Good Evening"
        return "Good Night"
