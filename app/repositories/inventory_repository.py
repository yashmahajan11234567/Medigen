from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload

from app.models.inventory import InventoryItem
from app.models.medicine import Medicine
from app.repositories.base import BaseRepository


class InventoryRepository(BaseRepository):
    def add_inventory_item(self, inventory_item: InventoryItem) -> InventoryItem:
        self.session.add(inventory_item)
        self.session.commit()
        self.session.refresh(inventory_item)
        return inventory_item

    def update_inventory_item(self, inventory_item: InventoryItem) -> InventoryItem:
        self.session.add(inventory_item)
        self.session.commit()
        self.session.refresh(inventory_item)
        return inventory_item

    def soft_delete_inventory_item(self, inventory_item: InventoryItem) -> None:
        inventory_item.is_deleted = True
        inventory_item.deleted_at = func.now()
        self.session.add(inventory_item)
        self.session.commit()

    def get_inventory_item_by_id(self, *, user_id: int, inventory_id: int) -> InventoryItem | None:
        statement = (
            select(InventoryItem)
            .options(joinedload(InventoryItem.medicine))
            .where(
                InventoryItem.id == inventory_id,
                InventoryItem.user_id == user_id,
                InventoryItem.is_deleted.is_(False),
            )
        )
        return self.session.execute(statement).scalar_one_or_none()

    def list_inventory_items(self, *, user_id: int) -> list[InventoryItem]:
        statement = (
            select(InventoryItem)
            .options(joinedload(InventoryItem.medicine))
            .where(
                InventoryItem.user_id == user_id,
                InventoryItem.is_deleted.is_(False),
            )
            .order_by(InventoryItem.created_at.desc(), InventoryItem.id.desc())
        )
        return list(self.session.execute(statement).scalars().unique().all())

    def search_medicines(self, *, user_id: int, query: str) -> list[InventoryItem]:
        normalized_query = f"%{query.strip().lower()}%"
        statement = (
            select(InventoryItem)
            .join(InventoryItem.medicine)
            .options(joinedload(InventoryItem.medicine))
            .where(
                InventoryItem.user_id == user_id,
                InventoryItem.is_deleted.is_(False),
                Medicine.is_deleted.is_(False),
                or_(
                    func.lower(Medicine.name).like(normalized_query),
                    func.lower(func.coalesce(Medicine.generic_name, "")).like(normalized_query),
                ),
            )
            .order_by(InventoryItem.created_at.desc(), InventoryItem.id.desc())
        )
        return list(self.session.execute(statement).scalars().unique().all())

    def filter_medicines(
        self,
        *,
        user_id: int,
        statuses: list[str] | None = None,
        medicine_type: str | None = None,
    ) -> list[InventoryItem]:
        statement = (
            select(InventoryItem)
            .join(InventoryItem.medicine)
            .options(joinedload(InventoryItem.medicine))
            .where(
                InventoryItem.user_id == user_id,
                InventoryItem.is_deleted.is_(False),
                Medicine.is_deleted.is_(False),
            )
        )
        if statuses:
            statement = statement.where(InventoryItem.status.in_(statuses))
        if medicine_type:
            statement = statement.where(Medicine.dosage_form == medicine_type)
        statement = statement.order_by(InventoryItem.created_at.desc(), InventoryItem.id.desc())
        return list(self.session.execute(statement).scalars().unique().all())

    def get_duplicate_inventory_item(
        self,
        *,
        user_id: int,
        medicine_id: int,
        expiry_date: date | None,
        exclude_inventory_id: int | None = None,
    ) -> InventoryItem | None:
        statement = select(InventoryItem).where(
            InventoryItem.user_id == user_id,
            InventoryItem.medicine_id == medicine_id,
            InventoryItem.expiry_date == expiry_date,
            InventoryItem.is_deleted.is_(False),
        )
        if exclude_inventory_id is not None:
            statement = statement.where(InventoryItem.id != exclude_inventory_id)
        return self.session.execute(statement).scalar_one_or_none()

    def get_inventory_summary(self, *, user_id: int) -> dict[str, int]:
        counts = self._count_by_status(user_id=user_id)
        return {
            "total_medicines": counts["total"],
            "available_medicines": counts["available"] + counts["low_stock"],
            "finished_medicines": counts["out_of_stock"],
            "expiring_soon": counts["expiring_soon"],
            "expired": counts["expired"],
        }

    def get_expiring_medicines(self, *, user_id: int) -> list[InventoryItem]:
        statement = (
            select(InventoryItem)
            .options(joinedload(InventoryItem.medicine))
            .where(
                InventoryItem.user_id == user_id,
                InventoryItem.is_deleted.is_(False),
                InventoryItem.expiry_date.is_not(None),
            )
            .order_by(InventoryItem.expiry_date.asc(), InventoryItem.id.asc())
        )
        return list(self.session.execute(statement).scalars().unique().all())

    def _count_by_status(self, *, user_id: int) -> dict[str, int]:
        statement = (
            select(InventoryItem.status, func.count(InventoryItem.id))
            .where(
                InventoryItem.user_id == user_id,
                InventoryItem.is_deleted.is_(False),
            )
            .group_by(InventoryItem.status)
        )
        result = {status: 0 for status in ["available", "low_stock", "expiring_soon", "expired", "out_of_stock"]}
        total = 0
        for status, count in self.session.execute(statement).all():
            result[str(status)] = int(count)
            total += int(count)
        result["total"] = total
        return result

