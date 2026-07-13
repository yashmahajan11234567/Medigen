from datetime import date, timedelta

from app.core.enums import InventoryStatus, MedicineType
from app.repositories.inventory_repository import InventoryRepository
from tests.support import create_inventory_item, create_medicine, create_user


def test_inventory_repository_supports_listing_search_filters_and_summary(db_session):
    user = create_user(db_session, email="inventory-repo@example.com")
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
    available_item = create_inventory_item(
        db_session,
        user_id=user.id,
        medicine_id=tablet.id,
        status=InventoryStatus.AVAILABLE,
        quantity=10,
        expiry_date=date.today() + timedelta(days=90),
    )
    expiring_item = create_inventory_item(
        db_session,
        user_id=user.id,
        medicine_id=syrup.id,
        status=InventoryStatus.EXPIRING_SOON,
        expiry_date=date.today() + timedelta(days=7),
    )

    repository = InventoryRepository(db_session)

    listed = repository.list_inventory_items(user_id=user.id)
    searched = repository.search_medicines(user_id=user.id, query="para")
    filtered = repository.filter_medicines(
        user_id=user.id,
        statuses=[InventoryStatus.EXPIRING_SOON.value],
    )
    summary = repository.get_inventory_summary(user_id=user.id)
    expiring = repository.get_expiring_medicines(user_id=user.id)
    duplicate = repository.get_duplicate_inventory_item(
        user_id=user.id,
        medicine_id=tablet.id,
        expiry_date=available_item.expiry_date,
    )

    assert len(listed) == 2
    assert [item.id for item in searched] == [available_item.id]
    assert [item.id for item in filtered] == [expiring_item.id]
    assert summary["total_medicines"] == 2
    assert summary["expiring_soon"] == 1
    assert [item.id for item in expiring] == [expiring_item.id, available_item.id]
    assert duplicate is not None

