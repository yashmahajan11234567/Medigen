from datetime import date

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
        expiring_statement = select(func.count(InventoryItem.id)).where(
            InventoryItem.user_id == user_id,
            InventoryItem.is_deleted.is_(False),
            InventoryItem.status == InventoryStatus.EXPIRING_SOON,
        )

        return {
            "total_medicines": int(self.session.execute(total_statement).scalar_one()),
            "expiring_soon": int(self.session.execute(expiring_statement).scalar_one()),
        }

