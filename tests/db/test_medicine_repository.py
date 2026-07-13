from app.core.enums import MedicineType
from app.repositories.medicine_repository import MedicineRepository
from tests.support import create_medicine


def test_medicine_repository_search_and_exact_lookup(db_session):
    branded = create_medicine(
        db_session,
        name="Crocin 500",
        generic_name="Paracetamol",
        brand_name="Crocin 500",
        composition="Paracetamol",
        strength="500",
        unit="MG",
        dosage_form=MedicineType.TABLET,
        route="Oral",
    )
    generic = create_medicine(
        db_session,
        name="Paracetamol 500 Generic",
        generic_name="Paracetamol",
        brand_name=None,
        composition=" paracetamol ",
        strength="500.0",
        unit="mg",
        dosage_form=MedicineType.TABLET,
        route=" oral ",
    )
    create_medicine(
        db_session,
        name="Ibuprofen 400 Generic",
        generic_name="Ibuprofen",
        brand_name=None,
        composition="Ibuprofen",
        strength="400",
        unit="mg",
        dosage_form=MedicineType.TABLET,
        route="oral",
    )

    repository = MedicineRepository(db_session)

    branded_results = repository.search_branded_medicine("  crocin 500 ")
    exact_matches = repository.exact_composition_lookup(
        ingredient="paracetamol",
        strength="500.0",
        unit="mg",
        dosage_form="tablet",
        route="oral",
    )
    all_generics = repository.get_generic_medicines()
    by_canonical = repository.get_medicines_by_canonical_composition(
        ingredient="paracetamol",
        strength="500.0",
        unit="mg",
        dosage_form="tablet",
        route="oral",
    )

    assert [item.id for item in branded_results] == [branded.id]
    assert [item.id for item in exact_matches] == [generic.id]
    assert generic.id in [item.id for item in all_generics]
    assert branded.id in [item.id for item in by_canonical]

