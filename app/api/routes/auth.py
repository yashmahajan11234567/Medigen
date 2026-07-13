from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_active_user
from app.db.session import DbSession
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserRead
from app.services.auth_service import AuthService


router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterRequest, db: DbSession) -> UserRead:
    service = AuthService(db)
    return UserRead.model_validate(service.register_user(payload))


@router.post("/login", response_model=TokenResponse)
def login_user(payload: LoginRequest, db: DbSession) -> TokenResponse:
    service = AuthService(db)
    token, user = service.authenticate_user(payload)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserRead.model_validate(user),
    )


@router.get("/me", response_model=UserRead)
def read_current_user(current_user=Depends(get_current_active_user)) -> UserRead:
    return UserRead.model_validate(current_user)

