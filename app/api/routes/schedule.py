from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_active_user
from app.db.session import DbSession
from app.schemas.schedule import (
    BillMedicineInput,
    ScheduleCompleteRequest,
    ScheduleCreateRequest,
    ScheduleDeleteResponse,
    ScheduleListResponse,
    ScheduleReminderResponse,
    ScheduleResponse,
    ScheduleUpdateRequest,
)
from app.services.scheduler_service import SchedulerService


router = APIRouter()


@router.get("/today", response_model=ScheduleListResponse)
def get_todays_schedule(
    db: DbSession,
    current_user=Depends(get_current_active_user),
) -> ScheduleListResponse:
    return SchedulerService(db).get_todays_schedule(user_id=current_user.id)


@router.post("/from-bill", response_model=ScheduleResponse, status_code=201)
def create_schedule_from_bill(
    payload: BillMedicineInput,
    db: DbSession,
    current_user=Depends(get_current_active_user),
) -> ScheduleResponse:
    return SchedulerService(db).create_schedule_from_bill(user_id=current_user.id, payload=payload)


@router.post("/complete", response_model=ScheduleReminderResponse)
def complete_schedule_reminder(
    payload: ScheduleCompleteRequest,
    db: DbSession,
    current_user=Depends(get_current_active_user),
) -> ScheduleReminderResponse:
    return SchedulerService(db).complete_reminder(user_id=current_user.id, payload=payload)


@router.get("", response_model=ScheduleListResponse)
def list_schedules(
    db: DbSession,
    current_user=Depends(get_current_active_user),
) -> ScheduleListResponse:
    return SchedulerService(db).list_schedules(user_id=current_user.id)


@router.post("", response_model=ScheduleResponse, status_code=201)
def create_schedule(
    payload: ScheduleCreateRequest,
    db: DbSession,
    current_user=Depends(get_current_active_user),
) -> ScheduleResponse:
    return SchedulerService(db).create_schedule(user_id=current_user.id, payload=payload)


@router.get("/{schedule_id}", response_model=ScheduleResponse)
def get_schedule(
    schedule_id: int,
    db: DbSession,
    current_user=Depends(get_current_active_user),
) -> ScheduleResponse:
    return SchedulerService(db).get_schedule(user_id=current_user.id, schedule_id=schedule_id)


@router.put("/{schedule_id}", response_model=ScheduleResponse)
def update_schedule(
    schedule_id: int,
    payload: ScheduleUpdateRequest,
    db: DbSession,
    current_user=Depends(get_current_active_user),
) -> ScheduleResponse:
    return SchedulerService(db).update_schedule(
        user_id=current_user.id,
        schedule_id=schedule_id,
        payload=payload,
    )


@router.delete("/{schedule_id}", response_model=ScheduleDeleteResponse)
def delete_schedule(
    schedule_id: int,
    db: DbSession,
    current_user=Depends(get_current_active_user),
) -> ScheduleDeleteResponse:
    return SchedulerService(db).delete_schedule(user_id=current_user.id, schedule_id=schedule_id)
