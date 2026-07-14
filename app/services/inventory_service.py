from datetime import date, timedelta

from app.core.enums import InventoryStatus, MedicineType, ReminderPeriod
from app.core.exceptions import AppException
from app.models.inventory import InventoryItem
from app.models.medicine import Medicine
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.medicine_repository import MedicineRepository
from app.schemas.inventory import (
    InventoryCreateRequest,
    InventoryDeleteResponse,
    InventoryListResponse,
    InventoryResponseItem,
    InventorySummaryResponse,
    InventoryUpdateRequest,
)


QUANTITY_TRACKED_TYPES = {MedicineType.TABLET, MedicineType.CAPSULE}
AVAILABILITY_TRACKED_TYPES = {
    MedicineType.SYRUP,
    MedicineType.CREAM,
    MedicineType.OINTMENT,
    MedicineType.INJECTION,
    MedicineType.DROPS,
}


class InventoryService:
    def __init__(self, session) -> None:
        self.inventory_repository = InventoryRepository(session)
        self.medicine_repository = MedicineRepository(session)

    def list_inventory(self, *, user_id: int) -> InventoryListResponse:
        items = [self._sync_status(item) for item in self.inventory_repository.list_inventory_items(user_id=user_id)]
        return InventoryListResponse(items=[self._to_response(item) for item in items])

    def get_inventory_item(self, *, user_id: int, inventory_id: int) -> InventoryResponseItem:
        item = self.inventory_repository.get_inventory_item_by_id(user_id=user_id, inventory_id=inventory_id)
        if item is None:
            raise AppException("Inventory medicine not found.", 404, "inventory_medicine_not_found")
        item = self._sync_status(item)
        return self._to_response(item)

    def create_inventory_item(self, *, user_id: int, payload: InventoryCreateRequest) -> InventoryResponseItem:
        self._validate_dates(expiry_date=payload.expiry_date, purchase_date=payload.purchase_date)
        medicine = self._resolve_or_create_medicine(payload)
        self._validate_quantity_rules(medicine_type=medicine.dosage_form, quantity=payload.quantity)
        self._ensure_no_duplicate(user_id=user_id, medicine_id=medicine.id, expiry_date=payload.expiry_date)

        item = InventoryItem(
            user_id=user_id,
            medicine_id=medicine.id,
            quantity=payload.quantity,
            quantity_unit=payload.quantity_unit,
            expiry_date=payload.expiry_date,
            purchase_date=payload.purchase_date,
            image_url=payload.image_path,
            notes=payload.notes,
            status=self._determine_status(
                medicine_type=medicine.dosage_form,
                quantity=payload.quantity,
                expiry_date=payload.expiry_date,
            ),
        )
        created = self.inventory_repository.add_inventory_item(item)
        created = self._load_inventory_item(user_id=user_id, inventory_id=created.id)
        return self._to_response(created)

    def update_inventory_item(
        self,
        *,
        user_id: int,
        inventory_id: int,
        payload: InventoryUpdateRequest,
    ) -> InventoryResponseItem:
        item = self._load_inventory_item(user_id=user_id, inventory_id=inventory_id)

        medicine = item.medicine
        if payload.name is not None:
            medicine.name = payload.name
        if payload.generic_name is not None:
            medicine.generic_name = payload.generic_name
        if payload.brand_name is not None:
            medicine.brand_name = payload.brand_name
        if payload.type is not None:
            medicine.dosage_form = payload.type

        updated_quantity = payload.quantity if payload.quantity is not None else item.quantity
        updated_expiry = payload.expiry_date if payload.expiry_date is not None else item.expiry_date
        updated_purchase = payload.purchase_date if payload.purchase_date is not None else item.purchase_date

        self._validate_dates(expiry_date=updated_expiry, purchase_date=updated_purchase)
        self._validate_quantity_rules(medicine_type=medicine.dosage_form, quantity=updated_quantity)
        self._ensure_no_duplicate(
            user_id=user_id,
            medicine_id=medicine.id,
            expiry_date=updated_expiry,
            exclude_inventory_id=item.id,
        )

        item.quantity = updated_quantity
        if payload.quantity_unit is not None:
            item.quantity_unit = payload.quantity_unit
        item.expiry_date = updated_expiry
        item.purchase_date = updated_purchase
        if payload.image_path is not None:
            item.image_url = payload.image_path
        if payload.notes is not None:
            item.notes = payload.notes
        item.status = self._determine_status(
            medicine_type=medicine.dosage_form,
            quantity=item.quantity,
            expiry_date=item.expiry_date,
        )

        updated = self.inventory_repository.update_inventory_item(item)
        updated = self._load_inventory_item(user_id=user_id, inventory_id=updated.id)
        return self._to_response(updated)

    def delete_inventory_item(self, *, user_id: int, inventory_id: int) -> InventoryDeleteResponse:
        item = self._load_inventory_item(user_id=user_id, inventory_id=inventory_id)
        self.inventory_repository.soft_delete_inventory_item(item)
        return InventoryDeleteResponse(message="Inventory medicine deleted successfully.")

    def search_inventory(self, *, user_id: int, query: str) -> InventoryListResponse:
        items = [self._sync_status(item) for item in self.inventory_repository.search_medicines(user_id=user_id, query=query)]
        return InventoryListResponse(items=[self._to_response(item) for item in items])

    def filter_inventory(
        self,
        *,
        user_id: int,
        status: str | None = None,
        medicine_type: MedicineType | None = None,
    ) -> InventoryListResponse:
        for item in self.inventory_repository.list_inventory_items(user_id=user_id):
            self._sync_status(item)
        statuses = self._map_filter_status(status)
        items = [
            self._sync_status(item)
            for item in self.inventory_repository.filter_medicines(
                user_id=user_id,
                statuses=statuses,
                medicine_type=medicine_type.value if medicine_type else None,
            )
        ]
        return InventoryListResponse(items=[self._to_response(item) for item in items])

    def get_inventory_summary(self, *, user_id: int) -> InventorySummaryResponse:
        items = self.inventory_repository.list_inventory_items(user_id=user_id)
        for item in items:
            self._sync_status(item)
        return InventorySummaryResponse(**self.inventory_repository.get_inventory_summary(user_id=user_id))

    def add_generic_medicine_to_inventory(
        self,
        *,
        user_id: int,
        medicine_id: int,
        expiry_date: date | None = None,
        quantity: float | None = None,
        quantity_unit: str | None = None,
        commit: bool = True,
    ) -> InventoryResponseItem:
        medicine = self.medicine_repository.get_medicine_by_id(medicine_id)
        if medicine is None:
            raise AppException("Medicine not found.", 404, "medicine_not_found")
        if quantity is None and medicine.dosage_form in QUANTITY_TRACKED_TYPES:
            quantity = 1
            quantity_unit = quantity_unit or "unit"
        self._validate_dates(expiry_date=expiry_date, purchase_date=None)
        self._validate_quantity_rules(medicine_type=medicine.dosage_form, quantity=quantity)
        self._ensure_no_duplicate(user_id=user_id, medicine_id=medicine.id, expiry_date=expiry_date)
        item = InventoryItem(
            user_id=user_id,
            medicine_id=medicine.id,
            quantity=quantity,
            quantity_unit=quantity_unit,
            expiry_date=expiry_date,
            status=self._determine_status(
                medicine_type=medicine.dosage_form,
                quantity=quantity,
                expiry_date=expiry_date,
            ),
        )
        created = self.inventory_repository.add_inventory_item(item, commit=commit)
        if not commit:
            return self._to_response(created)
        created = self._load_inventory_item(user_id=user_id, inventory_id=created.id)
        return self._to_response(created)

    def add_scheduler_medicine_to_inventory(
        self,
        *,
        user_id: int,
        medicine_id: int,
        quantity: float | None,
        quantity_unit: str | None,
        expiry_date: date | None = None,
        commit: bool = True,
    ) -> InventoryResponseItem:
        return self.add_generic_medicine_to_inventory(
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
        dose_quantity = self._dose_quantity_for_period(dosage_pattern=dosage_pattern, period=period)
        if dose_quantity <= 0:
            return None

        items = self.inventory_repository.list_inventory_items_by_medicine(
            user_id=user_id,
            medicine_id=medicine_id,
        )
        if not items:
            return None

        for item in items:
            item = self._sync_status(item, commit=commit)
            if item.medicine.dosage_form not in QUANTITY_TRACKED_TYPES:
                return None
            if item.quantity is None or item.quantity <= 0:
                continue

            item.quantity = max(item.quantity - dose_quantity, 0)
            item.status = self._determine_status(
                medicine_type=item.medicine.dosage_form,
                quantity=item.quantity,
                expiry_date=item.expiry_date,
            )
            updated = self.inventory_repository.update_inventory_item(item, commit=commit)
            if not commit:
                return self._to_response(updated)
            refreshed = self._load_inventory_item(user_id=user_id, inventory_id=updated.id)
            return self._to_response(refreshed)

        return None

    def _resolve_or_create_medicine(self, payload: InventoryCreateRequest) -> Medicine:
        if payload.medicine_id is not None:
            medicine = self.medicine_repository.get_medicine_by_id(payload.medicine_id)
            if medicine is None:
                raise AppException("Medicine not found.", 404, "medicine_not_found")
            return medicine

        if not payload.name:
            raise AppException(
                "Missing required fields: name is required when medicine_id is not provided.",
                422,
                "validation_error",
            )

        medicine = Medicine(
            name=payload.name,
            generic_name=payload.generic_name,
            brand_name=payload.brand_name,
            composition=payload.generic_name or payload.name,
            dosage_form=payload.type,
        )
        self.medicine_repository.session.add(medicine)
        self.medicine_repository.session.commit()
        self.medicine_repository.session.refresh(medicine)
        return medicine

    def _validate_dates(self, *, expiry_date: date | None, purchase_date: date | None) -> None:
        if expiry_date and purchase_date and expiry_date < purchase_date:
            raise AppException("Invalid expiry date.", 422, "invalid_expiry_date")

    def _validate_quantity_rules(self, *, medicine_type: MedicineType, quantity: float | None) -> None:
        if quantity is not None and quantity < 0:
            raise AppException("Negative quantities are not allowed.", 422, "invalid_quantity")
        if medicine_type in QUANTITY_TRACKED_TYPES and quantity is None:
            raise AppException(
                "Quantity is required for tablets and capsules.",
                422,
                "missing_required_fields",
            )

    def _ensure_no_duplicate(
        self,
        *,
        user_id: int,
        medicine_id: int,
        expiry_date: date | None,
        exclude_inventory_id: int | None = None,
    ) -> None:
        duplicate = self.inventory_repository.get_duplicate_inventory_item(
            user_id=user_id,
            medicine_id=medicine_id,
            expiry_date=expiry_date,
            exclude_inventory_id=exclude_inventory_id,
        )
        if duplicate is not None:
            raise AppException("Duplicate medicine entry found.", 409, "duplicate_medicine")

    def _determine_status(
        self,
        *,
        medicine_type: MedicineType,
        quantity: float | None,
        expiry_date: date | None,
    ) -> InventoryStatus:
        today = date.today()
        if expiry_date and expiry_date < today:
            return InventoryStatus.EXPIRED
        if expiry_date and expiry_date <= today + timedelta(days=30):
            return InventoryStatus.EXPIRING_SOON

        if medicine_type in QUANTITY_TRACKED_TYPES:
            if quantity is None or quantity <= 0:
                return InventoryStatus.OUT_OF_STOCK
            if quantity <= 5:
                return InventoryStatus.LOW_STOCK
            return InventoryStatus.AVAILABLE

        if medicine_type in AVAILABILITY_TRACKED_TYPES:
            if quantity is not None and quantity <= 0:
                return InventoryStatus.OUT_OF_STOCK
            return InventoryStatus.AVAILABLE

        if quantity is not None and quantity <= 0:
            return InventoryStatus.OUT_OF_STOCK
        return InventoryStatus.AVAILABLE

    def _sync_status(self, item: InventoryItem, *, commit: bool = True) -> InventoryItem:
        expected_status = self._determine_status(
            medicine_type=item.medicine.dosage_form,
            quantity=item.quantity,
            expiry_date=item.expiry_date,
        )
        if item.status != expected_status:
            item.status = expected_status
            item = self.inventory_repository.update_inventory_item(item, commit=commit)
        return item

    def _dose_quantity_for_period(self, *, dosage_pattern: str, period: ReminderPeriod) -> int:
        try:
            morning, afternoon, night = [int(part) for part in dosage_pattern.split("-")]
        except ValueError as exc:
            raise AppException("Invalid dosage.", 422, "invalid_dosage") from exc

        if period == ReminderPeriod.MORNING:
            return morning
        if period == ReminderPeriod.AFTERNOON:
            return afternoon
        return night

    def _to_response(self, item: InventoryItem) -> InventoryResponseItem:
        return InventoryResponseItem(
            id=item.id,
            medicine_id=item.medicine_id,
            name=item.medicine.name,
            generic_name=item.medicine.generic_name,
            brand_name=item.medicine.brand_name,
            type=item.medicine.dosage_form,
            quantity=item.quantity,
            quantity_unit=item.quantity_unit,
            status=item.status,
            expiry_date=item.expiry_date,
            purchase_date=item.purchase_date,
            image_path=item.image_url,
            notes=item.notes,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    def _load_inventory_item(self, *, user_id: int, inventory_id: int) -> InventoryItem:
        item = self.inventory_repository.get_inventory_item_by_id(user_id=user_id, inventory_id=inventory_id)
        if item is None:
            raise AppException("Inventory medicine not found.", 404, "inventory_medicine_not_found")
        return item

    def _map_filter_status(self, status: str | None) -> list[str] | None:
        if status is None:
            return None

        normalized = status.strip().lower().replace(" ", "_")
        if normalized in {"", "all"}:
            return None
        if normalized == "available":
            return [InventoryStatus.AVAILABLE.value, InventoryStatus.LOW_STOCK.value]
        if normalized == "finished":
            return [InventoryStatus.OUT_OF_STOCK.value]
        if normalized == "expiring_soon":
            return [InventoryStatus.EXPIRING_SOON.value]
        if normalized == "expired":
            return [InventoryStatus.EXPIRED.value]
        if normalized == "low_stock":
            return [InventoryStatus.LOW_STOCK.value]

        raise AppException("Invalid inventory filter.", 422, "invalid_inventory_filter")
