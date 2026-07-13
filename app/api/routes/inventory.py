from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import get_current_active_user
from app.core.enums import MedicineType
from app.db.session import DbSession
from app.schemas.inventory import (
    InventoryCreateRequest,
    InventoryDeleteResponse,
    InventoryListResponse,
    InventoryResponseItem,
    InventorySummaryResponse,
    InventoryUpdateRequest,
)
from app.services.inventory_service import InventoryService


router = APIRouter()


@router.get("/search", response_model=InventoryListResponse)
def search_inventory_items(
    db: DbSession,
    current_user=Depends(get_current_active_user),
    query: str = Query(min_length=1, max_length=255),
) -> InventoryListResponse:
    return InventoryService(db).search_inventory(user_id=current_user.id, query=query)


@router.get("/filter", response_model=InventoryListResponse)
def filter_inventory_items(
    db: DbSession,
    current_user=Depends(get_current_active_user),
    status: str | None = Query(default=None),
    medicine_type: MedicineType | None = Query(default=None, alias="type"),
) -> InventoryListResponse:
    return InventoryService(db).filter_inventory(
        user_id=current_user.id,
        status=status,
        medicine_type=medicine_type,
    )


@router.get("/summary", response_model=InventorySummaryResponse)
def get_inventory_summary(
    db: DbSession,
    current_user=Depends(get_current_active_user),
) -> InventorySummaryResponse:
    return InventoryService(db).get_inventory_summary(user_id=current_user.id)


@router.get("", response_model=InventoryListResponse)
def list_inventory_items(
    db: DbSession,
    current_user=Depends(get_current_active_user),
) -> InventoryListResponse:
    return InventoryService(db).list_inventory(user_id=current_user.id)


@router.post("", response_model=InventoryResponseItem, status_code=201)
def create_inventory_item(
    payload: InventoryCreateRequest,
    db: DbSession,
    current_user=Depends(get_current_active_user),
) -> InventoryResponseItem:
    return InventoryService(db).create_inventory_item(user_id=current_user.id, payload=payload)


@router.get("/{inventory_id}", response_model=InventoryResponseItem)
def get_inventory_item(
    inventory_id: int,
    db: DbSession,
    current_user=Depends(get_current_active_user),
) -> InventoryResponseItem:
    return InventoryService(db).get_inventory_item(user_id=current_user.id, inventory_id=inventory_id)


@router.put("/{inventory_id}", response_model=InventoryResponseItem)
def update_inventory_item(
    inventory_id: int,
    payload: InventoryUpdateRequest,
    db: DbSession,
    current_user=Depends(get_current_active_user),
) -> InventoryResponseItem:
    return InventoryService(db).update_inventory_item(
        user_id=current_user.id,
        inventory_id=inventory_id,
        payload=payload,
    )


@router.delete("/{inventory_id}", response_model=InventoryDeleteResponse)
def delete_inventory_item(
    inventory_id: int,
    db: DbSession,
    current_user=Depends(get_current_active_user),
) -> InventoryDeleteResponse:
    return InventoryService(db).delete_inventory_item(user_id=current_user.id, inventory_id=inventory_id)
