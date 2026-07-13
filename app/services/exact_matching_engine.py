from app.models.medicine import Medicine
from app.schemas.generic_finder import CanonicalComposition, GenericMedicineSummary
from app.services.composition_normalization_service import CompositionNormalizationService


class ExactMatchingEngine:
    def __init__(self, normalization_service: CompositionNormalizationService | None = None) -> None:
        self.normalization_service = normalization_service or CompositionNormalizationService()

    def find_exact_matches(
        self,
        source: CanonicalComposition,
        candidate_medicines: list[Medicine],
        *,
        limit: int = 5,
    ) -> list[GenericMedicineSummary]:
        matches: list[GenericMedicineSummary] = []

        for medicine in candidate_medicines:
            candidate = self.normalization_service.normalize_medicine(medicine)
            if self._is_exact_match(source, candidate):
                matches.append(
                    GenericMedicineSummary(
                        id=medicine.id,
                        name=medicine.name,
                        generic_name=medicine.generic_name,
                        brand_name=medicine.brand_name,
                        composition=candidate,
                    )
                )
                if len(matches) == limit:
                    break

        return matches

    def _is_exact_match(
        self,
        source: CanonicalComposition,
        candidate: CanonicalComposition,
    ) -> bool:
        return (
            source.ingredient == candidate.ingredient
            and source.strength == candidate.strength
            and source.unit == candidate.unit
            and source.dosage_form == candidate.dosage_form
            and source.route == candidate.route
        )

