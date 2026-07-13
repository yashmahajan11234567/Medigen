import pytest

from app.core.enums import MedicineType
from app.core.exceptions import AppException
from app.schemas.generic_finder import CanonicalComposition
from app.services.composition_normalization_service import CompositionNormalizationService
from tests.support import create_medicine


def test_normalization_service_builds_canonical_composition(db_session):
    medicine = create_medicine(
        db_session,
        name="Crocin 500",
        generic_name="Paracetamol",
        brand_name="Crocin 500",
        composition=" Paracetamol ",
        strength="500.0",
        unit=" MG ",
        dosage_form=MedicineType.TABLET,
        route=" Oral ",
    )
    service = CompositionNormalizationService()

    canonical = service.normalize_medicine(medicine)

    assert canonical == CanonicalComposition(
        ingredient="paracetamol",
        strength="500",
        unit="mg",
        dosage_form=MedicineType.TABLET,
        route="oral",
    )


def test_normalization_service_rejects_combination_medicines():
    service = CompositionNormalizationService()

    with pytest.raises(AppException) as exc_info:
        service.normalize_components(
            ingredient="paracetamol + caffeine",
            strength="500",
            unit="mg",
            dosage_form="tablet",
            route="oral",
        )

    assert exc_info.value.code == "unsupported_combination_medicine"


def test_normalization_service_requires_all_fields():
    service = CompositionNormalizationService()

    with pytest.raises(AppException) as exc_info:
        service.normalize_components(
            ingredient="paracetamol",
            strength=None,
            unit="mg",
            dosage_form="tablet",
            route="oral",
        )

    assert exc_info.value.code == "invalid_composition"

