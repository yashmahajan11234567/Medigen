from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import get_current_active_user
from app.db.session import DbSession
from app.schemas.generic_finder import (
    AddToInventoryRequest,
    AddToInventoryResponse,
    CanonicalComposition,
    GenericFinderSearchResponse,
    GenericMedicineDetailResponse,
)
from app.services.generic_finder_service import GenericFinderService


router = APIRouter()


@router.get("/search", response_model=GenericFinderSearchResponse)
def search_generic_medicines(
    db: DbSession,
    brand_name: str = Query(min_length=1, max_length=255),
) -> GenericFinderSearchResponse:
    service = GenericFinderService(db)
    return service.search_by_brand_name(brand_name)


@router.post("/scan", response_model=GenericFinderSearchResponse)
def scan_generic_medicine(
    payload: CanonicalComposition,
    db: DbSession,
) -> GenericFinderSearchResponse:
    service = GenericFinderService(db)
    return service.scan_by_composition(payload)


@router.get("/{medicine_id}", response_model=GenericMedicineDetailResponse)
def get_generic_medicine_details(
    medicine_id: int,
    db: DbSession,
) -> GenericMedicineDetailResponse:
    service = GenericFinderService(db)
    return service.get_medicine_details(medicine_id)


@router.post("/add-to-inventory", response_model=AddToInventoryResponse)
def add_generic_medicine_to_inventory(
    payload: AddToInventoryRequest,
    db: DbSession,
    current_user=Depends(get_current_active_user),
) -> AddToInventoryResponse:
    service = GenericFinderService(db)
    return service.add_to_inventory(
        user_id=current_user.id,
        medicine_id=payload.medicine_id,
        quantity=payload.quantity,
        quantity_unit=payload.quantity_unit,
        expiry_date=payload.expiry_date,
    )
