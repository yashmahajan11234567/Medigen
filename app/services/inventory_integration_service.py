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
    ) -> InventoryResponseItem:
        return self.inventory_service.add_generic_medicine_to_inventory(
            user_id=user_id,
            medicine_id=medicine_id,
            expiry_date=expiry_date,
            quantity=quantity,
            quantity_unit=quantity_unit,
        )

    def add_scheduler_medicine(
        self,
        *,
        user_id: int,
        medicine_id: int,
        quantity,
        quantity_unit,
        expiry_date=None,
    ) -> InventoryResponseItem:
        return self.inventory_service.add_scheduler_medicine_to_inventory(
            user_id=user_id,
            medicine_id=medicine_id,
            quantity=quantity,
            quantity_unit=quantity_unit,
            expiry_date=expiry_date,
        )
