from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppException
from app.models.inventory import InventoryItem
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import (
    DashboardInventorySummary,
    DashboardResponse,
    DashboardScheduleItem,
    DashboardUserSummary,
    LowStockMedicineItem,
)


class DashboardService:
    def __init__(self, session) -> None:
        self.repository = DashboardRepository(session)

    def get_dashboard(self, user_id: int, current_datetime: datetime | None = None) -> DashboardResponse:
        now = current_datetime or datetime.now(timezone.utc)

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
            inventory_summary = self.repository.get_inventory_summary(user_id)
            low_stock_items = self.repository.get_low_stock_medicines(user_id)
            medical_records_count = self.repository.get_medical_records_count(user_id)
            generic_searches_count = self.repository.get_generic_searches_count(user_id)
        except AppException:
            raise
        except SQLAlchemyError as exc:
            raise AppException(
                message="A database error occurred while loading the dashboard.",
                status_code=500,
                code="database_error",
            ) from exc

        low_stock_medicines = [
            LowStockMedicineItem(
                id=item.id,
                name=item.medicine.name,
                quantity=item.quantity,
                quantity_unit=item.quantity_unit,
                expiry_date=item.expiry_date.isoformat() if item.expiry_date else None,
            )
            for item in low_stock_items
        ]

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
                total_medicines=inventory_summary["total_medicines"],
                expiring_soon=inventory_summary["expiring_soon"],
            ),
            low_stock_medicines=low_stock_medicines,
            medical_records_count=medical_records_count,
            generic_searches_count=generic_searches_count,
        )

    def get_greeting(self, current_datetime: datetime | None = None) -> str:
        hour = (current_datetime or datetime.now(timezone.utc)).hour

        if 5 <= hour < 12:
            return "Good Morning"
        if 12 <= hour < 17:
            return "Good Afternoon"
        if 17 <= hour < 21:
            return "Good Evening"
        return "Good Night"
