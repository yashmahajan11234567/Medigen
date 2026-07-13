from datetime import date, timedelta

import pytest

from app.core.enums import InventoryStatus, MedicineType
from app.core.exceptions import AppException
from app.schemas.inventory import InventoryCreateRequest
from app.services.inventory_service import InventoryService
from tests.support import create_inventory_item, create_medicine, create_user


def test_inventory_service_creates_and_summarizes_inventory(db_session):
    user = create_user(db_session, email="inventory-service@example.com")
    service = InventoryService(db_session)

    created = service.create_inventory_item(
        user_id=user.id,
        payload=InventoryCreateRequest(
            name="Paracetamol 500",
            generic_name="Paracetamol",
            type=MedicineType.TABLET,
            quantity=12,
            quantity_unit="tablets",
            expiry_date=date.today() + timedelta(days=90),
        ),
    )

    summary = service.get_inventory_summary(user_id=user.id)

    assert created.name == "Paracetamol 500"
    assert created.status == InventoryStatus.AVAILABLE
    assert summary.total_medicines == 1
    assert summary.available_medicines == 1


def test_inventory_service_detects_finished_and_expired_states(db_session):
    user = create_user(db_session, email="inventory-status@example.com")
    tablet = create_medicine(db_session, name="Tablet", dosage_form=MedicineType.TABLET)
    cream = create_medicine(db_session, name="Cream", dosage_form=MedicineType.CREAM)
    create_inventory_item(
        db_session,
        user_id=user.id,
        medicine_id=tablet.id,
        quantity=0,
        status=InventoryStatus.AVAILABLE,
    )
    create_inventory_item(
        db_session,
        user_id=user.id,
        medicine_id=cream.id,
        expiry_date=date.today() - timedelta(days=1),
        status=InventoryStatus.AVAILABLE,
    )
    service = InventoryService(db_session)

    items = service.list_inventory(user_id=user.id).items

    assert {item.status for item in items} == {
        InventoryStatus.OUT_OF_STOCK,
        InventoryStatus.EXPIRED,
    }


def test_inventory_service_prevents_duplicates(db_session):
    user = create_user(db_session, email="inventory-duplicate@example.com")
    medicine = create_medicine(db_session, name="Duplicate", dosage_form=MedicineType.TABLET)
    create_inventory_item(
        db_session,
        user_id=user.id,
        medicine_id=medicine.id,
        quantity=10,
        expiry_date=date.today() + timedelta(days=30),
    )
    service = InventoryService(db_session)

    with pytest.raises(AppException) as exc_info:
        service.create_inventory_item(
            user_id=user.id,
            payload=InventoryCreateRequest(
                medicine_id=medicine.id,
                type=MedicineType.TABLET,
                quantity=10,
                expiry_date=date.today() + timedelta(days=30),
            ),
        )

    assert exc_info.value.code == "duplicate_medicine"


def test_inventory_service_validates_negative_quantities(db_session):
    user = create_user(db_session, email="inventory-negative@example.com")
    service = InventoryService(db_session)

    with pytest.raises(AppException) as exc_info:
        service.create_inventory_item(
            user_id=user.id,
            payload=InventoryCreateRequest(
                name="Bad Quantity",
                type=MedicineType.TABLET,
                quantity=-1,
            ),
        )

    assert exc_info.value.code in {"invalid_quantity", "validation_error"}


def test_inventory_service_supports_search_and_filter(db_session):
    user = create_user(db_session, email="inventory-search@example.com")
    tablet = create_medicine(
        db_session,
        name="Paracetamol 500",
        generic_name="Paracetamol",
        dosage_form=MedicineType.TABLET,
    )
    syrup = create_medicine(
        db_session,
        name="Cough Syrup",
        generic_name="Dextromethorphan",
        dosage_form=MedicineType.SYRUP,
    )
    create_inventory_item(
        db_session,
        user_id=user.id,
        medicine_id=tablet.id,
        quantity=2,
        status=InventoryStatus.AVAILABLE,
    )
    create_inventory_item(
        db_session,
        user_id=user.id,
        medicine_id=syrup.id,
        status=InventoryStatus.EXPIRING_SOON,
        expiry_date=date.today() + timedelta(days=10),
    )
    service = InventoryService(db_session)

    search_result = service.search_inventory(user_id=user.id, query="para")
    filter_result = service.filter_inventory(user_id=user.id, status="expiring soon")

    assert len(search_result.items) == 1
    assert search_result.items[0].name == "Paracetamol 500"
    assert len(filter_result.items) == 1
    assert filter_result.items[0].name == "Cough Syrup"
