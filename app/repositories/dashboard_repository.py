from datetime import date, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload

from app.core.enums import InventoryStatus, NotificationStatus, ScheduleStatus
from app.models.inventory import InventoryItem
from app.models.notification import Notification
from app.models.schedule import Schedule
from app.models.user import User
from app.repositories.base import BaseRepository


class DashboardRepository(BaseRepository):
    def get_user_by_id(self, user_id: int) -> User | None:
        statement = select(User).where(User.id == user_id, User.is_deleted.is_(False))
        return self.session.execute(statement).scalar_one_or_none()

    def get_unread_notification_count(self, user_id: int) -> int:
        statement = select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.is_deleted.is_(False),
            Notification.status.in_(
                [NotificationStatus.PENDING, NotificationStatus.SENT]
            ),
        )
        return int(self.session.execute(statement).scalar_one())

    def get_todays_schedule(self, user_id: int, target_date: date) -> list[Schedule]:
        statement = (
            select(Schedule)
            .options(joinedload(Schedule.medicine))
            .where(
                Schedule.user_id == user_id,
                Schedule.is_deleted.is_(False),
                Schedule.status == ScheduleStatus.ACTIVE,
                Schedule.start_date.is_not(None),
                Schedule.start_date <= target_date,
                or_(Schedule.end_date.is_(None), Schedule.end_date >= target_date),
            )
            .order_by(Schedule.reminder_time.is_(None), Schedule.reminder_time.asc(), Schedule.id.asc())
        )
        return list(self.session.execute(statement).scalars().unique().all())

    def get_inventory_summary(self, user_id: int) -> dict[str, int]:
        total_statement = select(func.count(InventoryItem.id)).where(
            InventoryItem.user_id == user_id,
            InventoryItem.is_deleted.is_(False),
        )
        # Compute expiring_soon based on expiry_date (<= 30 days from today), not status field
        # This avoids needing to sync status during reads (no writes on GET)
        expiry_threshold = date.today() + timedelta(days=30)
        expiring_statement = select(func.count(InventoryItem.id)).where(
            InventoryItem.user_id == user_id,
            InventoryItem.is_deleted.is_(False),
            InventoryItem.expiry_date.is_not(None),
            InventoryItem.expiry_date <= expiry_threshold,
        )

        return {
            "total_medicines": int(self.session.execute(total_statement).scalar_one()),
            "expiring_soon": int(self.session.execute(expiring_statement).scalar_one()),
        }

    def get_low_stock_medicines(self, user_id: int) -> list[InventoryItem]:
        statement = (
            select(InventoryItem)
            .options(joinedload(InventoryItem.medicine))
            .where(
                InventoryItem.user_id == user_id,
                InventoryItem.is_deleted.is_(False),
                InventoryItem.status == InventoryStatus.LOW_STOCK,
            )
            .order_by(InventoryItem.expiry_date.is_(None), InventoryItem.expiry_date.asc(), InventoryItem.id.asc())
        )
        return list(self.session.execute(statement).scalars().unique().all())

    def get_medical_records_count(self, user_id: int) -> int:
        from app.models.medical_record import MedicalRecord
        statement = select(func.count(MedicalRecord.id)).where(
            MedicalRecord.user_id == user_id,
            MedicalRecord.is_deleted.is_(False),
        )
        return int(self.session.execute(statement).scalar_one())

    def get_generic_searches_count(self, user_id: int) -> int:
        """Count distinct generic search IDs across all medical records.

        Uses DISTINCT at the database level to reduce transferred rows,
        then de-duplicates across JSON array elements in Python (JSON
        array unnesting is not portable across SQLite without the JSON1
        extension, so the final cross-array dedup remains in application
        code).
        """
        from app.models.medical_record import MedicalRecord
        statement = (
            select(MedicalRecord.linked_generic_search_ids)
            .where(
                MedicalRecord.user_id == user_id,
                MedicalRecord.is_deleted.is_(False),
                MedicalRecord.linked_generic_search_ids.is_not(None),
            )
            .distinct()
        )
        result = self.session.execute(statement).scalars().all()
        unique_ids: set[str] = set()
        for ids in result:
            if ids:
                unique_ids.update(ids)
        return len(unique_ids)
