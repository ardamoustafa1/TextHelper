import time
from typing import Dict, Tuple

import redis
from fastapi import Request
from fastapi.responses import ORJSONResponse

from app.core.config import settings


class RateLimiter:
    """
    Simple IP/user based rate limiter.
    Uses Redis if available, otherwise in-memory counters.
    """

    def __init__(self):
        self._memory_store: Dict[str, Tuple[int, float]] = {}
        self._window_seconds = int(
            __import__("os").getenv("RATE_LIMIT_WINDOW_SECONDS", "60")
        )
        self._max_requests = int(
            __import__("os").getenv("RATE_LIMIT_MAX_REQUESTS", "120")
        )

        self._redis_client = None
        try:
            self._redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=0,
                socket_connect_timeout=1,
            )
            # Lazy check; ignore errors
            self._redis_client.ping()
        except Exception:
            self._redis_client = None

    def _make_key(self, identifier: str) -> str:
        return f"rl:{identifier}"

    def is_allowed(self, identifier: str) -> bool:
        now = int(time.time())
        key = self._make_key(identifier)

        # Redis-backed implementation
        if self._redis_client:
            try:
                with self._redis_client.pipeline() as pipe:
                    pipe.incr(key, 1)
                    pipe.expire(key, self._window_seconds)
                    current, _ = pipe.execute()
                return int(current) <= self._max_requests
            except Exception:
                # Fallback to memory if Redis has issues
                pass

        # In-memory fallback
        count, start_ts = self._memory_store.get(key, (0, now))
        if now - start_ts >= self._window_seconds:
            # New window
            self._memory_store[key] = (1, now)
            return True

        count += 1
        self._memory_store[key] = (count, start_ts)
        return count <= self._max_requests


rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware enforcing basic rate limits.
    - Keyed by client IP + optional user_id query/header.
    - Health/docs endpoints are excluded.
    """
    path = request.url.path
    if path in {"/docs", "/openapi.json", "/api/v1/health", "/health", "/api/v1/metrics"}:
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    user_id = request.headers.get("X-User-Id") or request.query_params.get("user_id") or "anonymous"
    identifier = f"{client_ip}:{user_id}"

    if not rate_limiter.is_allowed(identifier):
        return ORJSONResponse(
            status_code=429,
            content={
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests. Please slow down.",
            },
        )

    return await call_next(request)

