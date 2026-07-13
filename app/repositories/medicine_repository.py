from decimal import Decimal, InvalidOperation

from sqlalchemy import func, or_, select

from app.models.medicine import Medicine
from app.repositories.base import BaseRepository


class MedicineRepository(BaseRepository):
    def search_branded_medicine(self, brand_name: str) -> list[Medicine]:
        normalized_query = brand_name.strip().lower()
        statement = (
            select(Medicine)
            .where(
                Medicine.is_deleted.is_(False),
                Medicine.brand_name.is_not(None),
                or_(
                    func.lower(func.trim(Medicine.brand_name)) == normalized_query,
                    func.lower(func.trim(Medicine.name)) == normalized_query,
                ),
            )
            .order_by(Medicine.name.asc(), Medicine.id.asc())
        )
        return list(self.session.execute(statement).scalars().all())

    def get_medicine_by_id(self, medicine_id: int) -> Medicine | None:
        statement = select(Medicine).where(
            Medicine.id == medicine_id,
            Medicine.is_deleted.is_(False),
        )
        return self.session.execute(statement).scalar_one_or_none()

    def get_medicines_by_canonical_composition(
        self,
        *,
        ingredient: str,
        strength: str,
        unit: str,
        dosage_form: str,
        route: str,
        limit: int | None = None,
    ) -> list[Medicine]:
        strength_variants = self._strength_variants(strength)
        statement = (
            select(Medicine)
            .where(
                Medicine.is_deleted.is_(False),
                func.lower(func.trim(func.coalesce(Medicine.composition, ""))) == ingredient,
                func.lower(func.trim(func.coalesce(Medicine.strength, ""))).in_(strength_variants),
                func.lower(func.trim(func.coalesce(Medicine.unit, ""))) == unit,
                Medicine.dosage_form == dosage_form,
                func.lower(func.trim(func.coalesce(Medicine.route, ""))) == route,
            )
            .order_by(Medicine.name.asc(), Medicine.id.asc())
        )
        if limit is not None:
            statement = statement.limit(limit)
        return list(self.session.execute(statement).scalars().all())

    def get_generic_medicines(self, limit: int | None = None) -> list[Medicine]:
        statement = (
            select(Medicine)
            .where(
                Medicine.is_deleted.is_(False),
                or_(Medicine.brand_name.is_(None), func.trim(Medicine.brand_name) == ""),
            )
            .order_by(Medicine.name.asc(), Medicine.id.asc())
        )
        if limit is not None:
            statement = statement.limit(limit)
        return list(self.session.execute(statement).scalars().all())

    def exact_composition_lookup(
        self,
        *,
        ingredient: str,
        strength: str,
        unit: str,
        dosage_form: str,
        route: str,
        limit: int = 5,
    ) -> list[Medicine]:
        strength_variants = self._strength_variants(strength)
        statement = (
            select(Medicine)
            .where(
                Medicine.is_deleted.is_(False),
                or_(Medicine.brand_name.is_(None), func.trim(Medicine.brand_name) == ""),
                func.lower(func.trim(func.coalesce(Medicine.composition, ""))) == ingredient,
                func.lower(func.trim(func.coalesce(Medicine.strength, ""))).in_(strength_variants),
                func.lower(func.trim(func.coalesce(Medicine.unit, ""))) == unit,
                Medicine.dosage_form == dosage_form,
                func.lower(func.trim(func.coalesce(Medicine.route, ""))) == route,
            )
            .order_by(Medicine.name.asc(), Medicine.id.asc())
            .limit(limit)
        )
        return list(self.session.execute(statement).scalars().all())

    def _strength_variants(self, strength: str) -> list[str]:
        normalized = strength.strip().lower()
        variants = {normalized}
        try:
            decimal_value = Decimal(normalized)
        except InvalidOperation:
            return list(variants)

        plain_value = format(decimal_value.normalize(), "f")
        if "." in plain_value:
            plain_value = plain_value.rstrip("0").rstrip(".")
        plain_value = plain_value or "0"
        variants.add(plain_value)
        variants.add(f"{plain_value}.0")
        variants.add(f"{plain_value}.00")
        return list(variants)
