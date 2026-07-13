from fastapi import Depends, HTTPException, Request, status
from jose import JWTError

from app.auth.jwt import decode_access_token
from app.db.session import DbSession
from app.repositories.user_repository import UserRepository


def get_current_user(request: Request, db: DbSession):
    token = request.headers.get("Authorization", "")
    if not token.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
        )

    raw_token = token.replace("Bearer ", "", 1).strip()
    try:
        payload = decode_access_token(raw_token)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
        ) from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )

    user = UserRepository(db).get_by_id(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user no longer exists.",
        )
    return user


def get_current_active_user(current_user=Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive users are not allowed to access this resource.",
        )
    return current_user

