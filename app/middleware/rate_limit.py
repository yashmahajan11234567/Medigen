"""In-memory sliding-window rate limiter for authentication endpoints."""

import time
import threading
from collections import defaultdict

from fastapi import Request, HTTPException


class RateLimiter:
    """Thread-safe sliding-window rate limiter keyed by client IP + action."""

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def _clean_window(self, key: str, now: float) -> None:
        cutoff = now - self._window_seconds
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]

    def is_allowed(self, key: str) -> tuple[bool, int]:
        """Return (allowed, retry_after_seconds)."""
        with self._lock:
            now = time.time()
            self._clean_window(key, now)
            if len(self._requests[key]) >= self._max_requests:
                oldest = self._requests[key][0]
                retry_after = int(self._window_seconds - (now - oldest)) + 1
                return False, retry_after
            self._requests[key].append(now)
            return True, 0


# Sensible defaults: 5 login attempts per 60 s, 3 registrations per 60 s
_login_limiter = RateLimiter(max_requests=5, window_seconds=60)
_register_limiter = RateLimiter(max_requests=3, window_seconds=60)


def reset_rate_limiters() -> None:
    """Reset in-memory rate limiter state (used by test fixtures)."""
    global _login_limiter, _register_limiter
    _login_limiter = RateLimiter(max_requests=5, window_seconds=60)
    _register_limiter = RateLimiter(max_requests=3, window_seconds=60)


def _client_key(request: Request, action: str) -> str:
    client_ip = (
        request.client.host
        if request.client and request.client.host
        else "unknown"
    )
    return f"{action}:{client_ip}"


async def login_rate_limit(request: Request) -> None:
    allowed, retry_after = _login_limiter.is_allowed(_client_key(request, "login"))
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )


async def register_rate_limit(request: Request) -> None:
    allowed, retry_after = _register_limiter.is_allowed(_client_key(request, "register"))
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many registration attempts. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )
