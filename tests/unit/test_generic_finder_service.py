import pytest

from app.core.constants import NO_EXACT_GENERIC_SUBSTITUTE_FOUND
from app.core.enums import MedicineType
from app.core.exceptions import AppException
from app.schemas.generic_finder import CanonicalComposition
from app.services.generic_finder_service import GenericFinderService
from tests.support import create_medicine, create_user


def test_generic_finder_service_search_returns_exact_matches_capped_at_five(db_session):
    create_medicine(
        db_session,
        name="Crocin 500",
        generic_name="Paracetamol",
        brand_name="Crocin 500",
        composition="Paracetamol",
        strength="500",
        unit="mg",
        dosage_form=MedicineType.TABLET,
        route="oral",
    )
    for index in range(6):
        create_medicine(
            db_session,
            name=f"Paracetamol Generic {index}",
            generic_name="Paracetamol",
            composition="Paracetamol",
            strength="500",
            unit="mg",
            dosage_form=MedicineType.TABLET,
            route="oral",
        )

    service = GenericFinderService(db_session)
    response = service.search_by_brand_name("Crocin 500")

    assert len(response.matches) == 5
    assert response.message == "Found 5 exact generic substitute(s)."


def test_generic_finder_service_returns_no_exact_match_message(db_session):
    create_medicine(
        db_session,
        name="Crocin 500",
        generic_name="Paracetamol",
        brand_name="Crocin 500",
        composition="Paracetamol",
        strength="500",
        unit="mg",
        dosage_form=MedicineType.TABLET,
        route="oral",
    )
    create_medicine(
        db_session,
        name="Paracetamol 650",
        generic_name="Paracetamol",
        composition="Paracetamol",
        strength="650",
        unit="mg",
        dosage_form=MedicineType.TABLET,
        route="oral",
    )

    service = GenericFinderService(db_session)
    response = service.search_by_brand_name("Crocin 500")

    assert response.matches == []
    assert response.message == NO_EXACT_GENERIC_SUBSTITUTE_FOUND


def test_generic_finder_service_scan_is_deterministic(db_session):
    create_medicine(
        db_session,
        name="Paracetamol Generic",
        generic_name="Paracetamol",
        composition="Paracetamol",
        strength="500",
        unit="mg",
        dosage_form=MedicineType.TABLET,
        route="oral",
    )
    service = GenericFinderService(db_session)
    payload = CanonicalComposition(
        ingredient=" Paracetamol ",
        strength="500.0",
        unit=" MG ",
        dosage_form=MedicineType.TABLET,
        route=" Oral ",
    )

    first = service.scan_by_composition(payload)
    second = service.scan_by_composition(payload)

    assert first == second
    assert len(first.matches) == 1


def test_generic_finder_service_handles_duplicate_branded_matches(db_session):
    create_medicine(
        db_session,
        name="Crocin 500 A",
        generic_name="Paracetamol",
        brand_name="Crocin 500",
        composition="Paracetamol",
        strength="500",
        unit="mg",
        dosage_form=MedicineType.TABLET,
        route="oral",
    )
    create_medicine(
        db_session,
        name="Crocin 500 B",
        generic_name="Paracetamol",
        brand_name="Crocin 500",
        composition="Paracetamol",
        strength="500",
        unit="mg",
        dosage_form=MedicineType.TABLET,
        route="oral",
    )

    service = GenericFinderService(db_session)

    with pytest.raises(AppException) as exc_info:
        service.search_by_brand_name("Crocin 500")

    assert exc_info.value.code == "duplicate_medicine"


def test_generic_finder_service_add_to_inventory_requires_generic_selection(db_session):
    user = create_user(db_session, email="generic-finder-user@example.com")
    branded = create_medicine(
        db_session,
        name="Crocin 500",
        generic_name="Paracetamol",
        brand_name="Crocin 500",
        composition="Paracetamol",
        strength="500",
        unit="mg",
        dosage_form=MedicineType.TABLET,
        route="oral",
    )

    service = GenericFinderService(db_session)

    with pytest.raises(AppException) as exc_info:
        service.add_to_inventory(user_id=user.id, medicine_id=branded.id)

    assert exc_info.value.code == "invalid_generic_selection"

