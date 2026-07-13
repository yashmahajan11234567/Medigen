from decimal import Decimal, InvalidOperation

from app.core.exceptions import AppException
from app.models.medicine import Medicine
from app.schemas.generic_finder import CanonicalComposition


class CompositionNormalizationService:
    def normalize_medicine(self, medicine: Medicine) -> CanonicalComposition:
        ingredient = medicine.composition or medicine.generic_name or medicine.name
        return self.normalize_components(
            ingredient=ingredient,
            strength=medicine.strength,
            unit=medicine.unit,
            dosage_form=medicine.dosage_form.value
            if hasattr(medicine.dosage_form, "value")
            else str(medicine.dosage_form),
            route=medicine.route,
        )

    def normalize_components(
        self,
        *,
        ingredient: str | None,
        strength: str | None,
        unit: str | None,
        dosage_form: str | None,
        route: str | None,
    ) -> CanonicalComposition:
        normalized_ingredient = self._normalize_text(ingredient, "ingredient")
        self._ensure_single_ingredient(normalized_ingredient)

        normalized_strength = self._normalize_strength(strength)
        normalized_unit = self._normalize_text(unit, "unit")
        normalized_route = self._normalize_text(route, "route")
        normalized_dosage_form = self._normalize_text(dosage_form, "dosage_form")

        return CanonicalComposition(
            ingredient=normalized_ingredient,
            strength=normalized_strength,
            unit=normalized_unit,
            dosage_form=normalized_dosage_form,
            route=normalized_route,
        )

    def _normalize_text(self, value: str | None, field_name: str) -> str:
        normalized = (value or "").strip().lower()
        if not normalized:
            raise AppException(
                message=f"Invalid composition: {field_name} is required.",
                status_code=422,
                code="invalid_composition",
            )
        return " ".join(normalized.split())

    def _normalize_strength(self, value: str | None) -> str:
        normalized = self._normalize_text(value, "strength")
        try:
            decimal_value = Decimal(normalized)
        except InvalidOperation:
            return normalized

        normalized_decimal = format(decimal_value.normalize(), "f")
        if "." in normalized_decimal:
            normalized_decimal = normalized_decimal.rstrip("0").rstrip(".")
        return normalized_decimal or "0"

    def _ensure_single_ingredient(self, ingredient: str) -> None:
        if any(delimiter in ingredient for delimiter in ["+", ",", "/", "&"]):
            raise AppException(
                message="Combination medicines are not supported in Version 1.",
                status_code=422,
                code="unsupported_combination_medicine",
            )
