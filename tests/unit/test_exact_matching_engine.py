from app.core.enums import MedicineType
from app.services.composition_normalization_service import CompositionNormalizationService
from app.services.exact_matching_engine import ExactMatchingEngine
from tests.support import create_medicine


def test_exact_matching_engine_only_returns_full_exact_matches(db_session):
    source = create_medicine(
        db_session,
        name="Source Brand",
        generic_name="Paracetamol",
        brand_name="Source Brand",
        composition="Paracetamol",
        strength="500",
        unit="mg",
        dosage_form=MedicineType.TABLET,
        route="oral",
    )
    exact_match = create_medicine(
        db_session,
        name="Exact Generic",
        generic_name="Paracetamol",
        composition="Paracetamol",
        strength="500",
        unit="mg",
        dosage_form=MedicineType.TABLET,
        route="oral",
    )
    create_medicine(
        db_session,
        name="Wrong Strength",
        generic_name="Paracetamol",
        composition="Paracetamol",
        strength="650",
        unit="mg",
        dosage_form=MedicineType.TABLET,
        route="oral",
    )
    create_medicine(
        db_session,
        name="Wrong Unit",
        generic_name="Paracetamol",
        composition="Paracetamol",
        strength="500",
        unit="ml",
        dosage_form=MedicineType.TABLET,
        route="oral",
    )
    create_medicine(
        db_session,
        name="Wrong Form",
        generic_name="Paracetamol",
        composition="Paracetamol",
        strength="500",
        unit="mg",
        dosage_form=MedicineType.SYRUP,
        route="oral",
    )
    create_medicine(
        db_session,
        name="Wrong Route",
        generic_name="Paracetamol",
        composition="Paracetamol",
        strength="500",
        unit="mg",
        dosage_form=MedicineType.TABLET,
        route="topical",
    )

    normalization_service = CompositionNormalizationService()
    source_canonical = normalization_service.normalize_medicine(source)
    candidates = db_session.query(type(exact_match)).filter(type(exact_match).brand_name.is_(None)).all()
    engine = ExactMatchingEngine(normalization_service)

    matches = engine.find_exact_matches(source_canonical, candidates)

    assert [item.name for item in matches] == ["Exact Generic"]

