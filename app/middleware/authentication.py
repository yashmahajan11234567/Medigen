from collections.abc import Awaitable, Callable

from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.auth.jwt import decode_access_token


class AuthenticationContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request.state.user_id = None
        request.state.auth_error = None

        header = request.headers.get("Authorization", "")
        if header.startswith("Bearer "):
            token = header.replace("Bearer ", "", 1).strip()
            try:
                payload = decode_access_token(token)
                request.state.user_id = payload.get("sub")
            except JWTError:
                request.state.auth_error = "invalid_token"

        return await call_next(request)

