from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.auth.jwt import create_access_token
from app.auth.password import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest


class AuthService:
    def __init__(self, session) -> None:
        self.user_repository = UserRepository(session)

    def register_user(self, payload: RegisterRequest) -> User:
        existing_user = self.user_repository.get_by_email(payload.email)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )

        return self.user_repository.create(
            full_name=payload.full_name,
            email=payload.email,
            password_hash=hash_password(payload.password),
        )

    def authenticate_user(self, payload: LoginRequest) -> tuple[str, User]:
        user = self.user_repository.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        user.last_login_at = datetime.now(timezone.utc)
        self.user_repository.session.add(user)
        self.user_repository.session.commit()
        self.user_repository.session.refresh(user)

        token = create_access_token(subject=str(user.id))
        return token, user

