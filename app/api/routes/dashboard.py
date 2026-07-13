from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_active_user
from app.db.session import DbSession
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import DashboardService


router = APIRouter()


@router.get(
    "",
    response_model=DashboardResponse,
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)
def get_dashboard(db: DbSession, current_user=Depends(get_current_active_user)) -> DashboardResponse:
    service = DashboardService(db)
    return service.get_dashboard(current_user.id)
