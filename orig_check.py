from app.core.constants import NO_EXACT_GENERIC_SUBSTITUTE_FOUND
from app.core.exceptions import AppException
from app.repositories.medicine_repository import MedicineRepository
from app.schemas.generic_finder import (
    AddToInventoryResponse,
    CanonicalComposition,
    GenericFinderSearchResponse,
    GenericMedicineDetailResponse,
    GenericMedicineSummary,
)
from app.services.composition_normalization_service import CompositionNormalizationService
from app.services.exact_matching_engine import ExactMatchingEngine
from app.services.inventory_integration_service import InventoryIntegrationService


class GenericFinderService:
    def __init__(
        self,
        session,
        *,
        normalization_service: CompositionNormalizationService | None = None,
        matching_engine: ExactMatchingEngine | None = None,
        inventory_integration_service: InventoryIntegrationService | None = None,
    ) -> None:
        self.session = session
        self.repository = MedicineRepository(session)
        self.normalization_service = normalization_service or CompositionNormalizationService()
        self.matching_engine = matching_engine or ExactMatchingEngine(self.normalization_service)
        self.inventory_integration_service = (
            inventory_integration_service or InventoryIntegrationService(session)
        )

    def search_by_brand_name(self, brand_name: str) -> GenericFinderSearchResponse:
        medicines = self.repository.search_branded_medicine(brand_name)
        if not medicines:
            raise AppException(
                message="Medicine not found.",
                status_code=404,
                code="medicine_not_found",
            )
        if len(medicines) > 1:
            raise AppException(
                message="Duplicate branded medicines found for this search.",
                status_code=409,
                code="duplicate_medicine",
            )

        source_medicine = medicines[0]
        normalized = self.normalization_service.normalize_medicine(source_medicine)
        candidates = self.repository.exact_composition_lookup(
            ingredient=normalized.ingredient,
            strength=normalized.strength,
            unit=normalized.unit,
            dosage_form=normalized.dosage_form.value,
            route=normalized.route,
            limit=10,
        )
        matches = self.matching_engine.find_exact_matches(normalized, candidates, limit=5)

        return GenericFinderSearchResponse(
            source_medicine=self._to_summary(source_medicine, normalized),
            normalized_composition=normalized,
            matches=matches,
            message=(
                f"Found {len(matches)} exact generic substitute(s)."
                if matches
                else NO_EXACT_GENERIC_SUBSTITUTE_FOUND
            ),
        )

    def scan_by_composition(self, composition: CanonicalComposition) -> GenericFinderSearchResponse:
        normalized = self.normalization_service.normalize_components(
            ingredient=composition.ingredient,
            strength=composition.strength,
            unit=composition.unit,
            dosage_form=composition.dosage_form.value,
            route=composition.route,
        )
        candidates = self.repository.exact_composition_lookup(
            ingredient=normalized.ingredient,
            strength=normalized.strength,
            unit=normalized.unit,
            dosage_form=normalized.dosage_form.value,
            route=normalized.route,
            limit=10,
        )
        matches = self.matching_engine.find_exact_matches(normalized, candidates, limit=5)

        return GenericFinderSearchResponse(
            source_medicine=None,
            normalized_composition=normalized,
            matches=matches,
            message=(
                f"Found {len(matches)} exact generic substitute(s)."
                if matches
                else NO_EXACT_GENERIC_SUBSTITUTE_FOUND
            ),
        )

    def get_medicine_details(self, medicine_id: int) -> GenericMedicineDetailResponse:
        medicine = self.repository.get_medicine_by_id(medicine_id)
        if medicine is None:
            raise AppException(
                message="Medicine not found.",
                status_code=404,
                code="medicine_not_found",
            )

        normalized = self.normalization_service.normalize_medicine(medicine)
        return GenericMedicineDetailResponse(
            medicine=self._to_summary(medicine, normalized),
            is_generic=self._is_generic_medicine(medicine),
        )

    def add_to_inventory(
        self,
        *,
        user_id: int,
        medicine_id: int,
        quantity: float | None = None,
        quantity_unit: str | None = None,
        expiry_date=None,
    ) -> AddToInventoryResponse:
        medicine = self.repository.get_medicine_by_id(medicine_id)
        if medicine is None:
            raise AppException(
                message="Medicine not found.",
                status_code=404,
                code="medicine_not_found",
            )
        if not self._is_generic_medicine(medicine):
            raise AppException(
                message="Only generic medicines can be added through this endpoint.",
                status_code=422,
                code="invalid_generic_selection",
            )

        self.inventory_integration_service.add_generic_medicine(
            user_id=user_id,
            medicine_id=medicine_id,
            quantity=quantity,
            quantity_unit=quantity_unit,
            expiry_date=expiry_date,
        )
        return AddToInventoryResponse(
            message="Medicine added to inventory.",
            medicine_id=medicine_id,
        )

    def _to_summary(
        self,
        medicine,
        normalized: CanonicalComposition,
    ) -> GenericMedicineSummary:
        return GenericMedicineSummary(
            id=medicine.id,
            name=medicine.name,
            generic_name=medicine.generic_name,
            brand_name=medicine.brand_name,
            composition=normalized,
        )

    def _is_generic_medicine(self, medicine) -> bool:
        return medicine.brand_name is None or not medicine.brand_name.strip()
