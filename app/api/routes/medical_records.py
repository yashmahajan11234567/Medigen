from datetime import date

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import get_current_active_user
from app.core.enums import MedicalRecordDocumentType
from app.db.session import DbSession
from app.schemas.medical_records import (
    MedicalRecordCreateRequest,
    MedicalRecordDeleteResponse,
    MedicalRecordLinkRequest,
    MedicalRecordListResponse,
    MedicalRecordResponse,
    MedicalRecordUpdateRequest,
)
from app.services.medical_record_service import MedicalRecordService


router = APIRouter()


@router.get("/search", response_model=MedicalRecordListResponse)
def search_medical_records(
    db: DbSession,
    current_user=Depends(get_current_active_user),
    query: str = Query(min_length=1, max_length=255),
) -> MedicalRecordListResponse:
    return MedicalRecordService(db).search_records(user_id=current_user.id, query=query)


@router.get("/filter", response_model=MedicalRecordListResponse)
def filter_medical_records(
    db: DbSession,
    current_user=Depends(get_current_active_user),
    document_type: MedicalRecordDocumentType | None = Query(default=None),
    hospital: str | None = Query(default=None, max_length=255),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
) -> MedicalRecordListResponse:
    return MedicalRecordService(db).filter_records(
        user_id=current_user.id,
        document_type=document_type,
        hospital=hospital,
        date_from=date_from,
        date_to=date_to,
    )


@router.post("/link", response_model=MedicalRecordResponse)
def link_medical_record_modules(
    payload: MedicalRecordLinkRequest,
    db: DbSession,
    current_user=Depends(get_current_active_user),
) -> MedicalRecordResponse:
    return MedicalRecordService(db).link_modules(user_id=current_user.id, payload=payload)


@router.get("", response_model=MedicalRecordListResponse)
def list_medical_records(
    db: DbSession,
    current_user=Depends(get_current_active_user),
) -> MedicalRecordListResponse:
    return MedicalRecordService(db).list_records(user_id=current_user.id)


@router.post("", response_model=MedicalRecordResponse, status_code=201)
def create_medical_record(
    payload: MedicalRecordCreateRequest,
    db: DbSession,
    current_user=Depends(get_current_active_user),
) -> MedicalRecordResponse:
    return MedicalRecordService(db).create_record(user_id=current_user.id, payload=payload)


@router.get("/{record_id}", response_model=MedicalRecordResponse)
def get_medical_record(
    record_id: int,
    db: DbSession,
    current_user=Depends(get_current_active_user),
) -> MedicalRecordResponse:
    return MedicalRecordService(db).get_record(user_id=current_user.id, record_id=record_id)


@router.put("/{record_id}", response_model=MedicalRecordResponse)
def update_medical_record(
    record_id: int,
    payload: MedicalRecordUpdateRequest,
    db: DbSession,
    current_user=Depends(get_current_active_user),
) -> MedicalRecordResponse:
    return MedicalRecordService(db).update_record(
        user_id=current_user.id,
        record_id=record_id,
        payload=payload,
    )


@router.delete("/{record_id}", response_model=MedicalRecordDeleteResponse)
def delete_medical_record(
    record_id: int,
    db: DbSession,
    current_user=Depends(get_current_active_user),
) -> MedicalRecordDeleteResponse:
    return MedicalRecordService(db).delete_record(user_id=current_user.id, record_id=record_id)
