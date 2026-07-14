from app.core.enums import ReminderPeriod
from app.schemas.inventory import InventoryResponseItem
from app.services.inventory_service import InventoryService


class InventoryIntegrationService:
    def __init__(self, session) -> None:
        self.inventory_service = InventoryService(session)

    def add_generic_medicine(
        self,
        *,
        user_id: int,
        medicine_id: int,
        expiry_date=None,
        quantity=None,
        quantity_unit=None,
        commit: bool = True,
    ) -> InventoryResponseItem:
        return self.inventory_service.add_generic_medicine_to_inventory(
            user_id=user_id,
            medicine_id=medicine_id,
            expiry_date=expiry_date,
            quantity=quantity,
            quantity_unit=quantity_unit,
            commit=commit,
        )

    def add_scheduler_medicine(
        self,
        *,
        user_id: int,
        medicine_id: int,
        quantity,
        quantity_unit,
        expiry_date=None,
        commit: bool = True,
    ) -> InventoryResponseItem:
        return self.inventory_service.add_scheduler_medicine_to_inventory(
            user_id=user_id,
            medicine_id=medicine_id,
            quantity=quantity,
            quantity_unit=quantity_unit,
            expiry_date=expiry_date,
            commit=commit,
        )

    def consume_scheduler_medicine(
        self,
        *,
        user_id: int,
        medicine_id: int,
        dosage_pattern: str,
        period: ReminderPeriod,
        commit: bool = True,
    ) -> InventoryResponseItem | None:
        return self.inventory_service.consume_scheduler_medicine(
            user_id=user_id,
            medicine_id=medicine_id,
            dosage_pattern=dosage_pattern,
            period=period,
            commit=commit,
        )
