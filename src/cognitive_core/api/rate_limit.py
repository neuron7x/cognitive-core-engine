from __future__ import annotations

import logging
import threading
import time

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from ..config import settings

_redis_import_error: Exception | None = None

try:
    from ..rate_limiter import RedisBucketLimiter
except Exception as exc:
    RedisBucketLimiter = None  # type: ignore[assignment]
    _redis_import_error = exc
else:
    _redis_import_error = None


logger = logging.getLogger(__name__)


class InMemoryBucketLimiter:
    """Simple token bucket limiter stored in process memory."""

    def __init__(self, capacity: int, refill_per_sec: float) -> None:
        self.capacity = float(capacity)
        self.refill_per_sec = float(refill_per_sec)
        self._state: dict[str, tuple[float, float]] = {}
        self._lock = threading.Lock()

    def allow(self, token: str, needed: float = 1.0) -> bool:
        now = time.time()
        with self._lock:
            tokens, last_ts = self._state.get(token, (self.capacity, now))
            tokens = min(self.capacity, tokens + (now - last_ts) * self.refill_per_sec)
            allowed = tokens >= needed
            if allowed:
                tokens -= needed
            self._state[token] = (tokens, now)
            return allowed


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware enforcing simple token-bucket rate limits using Redis."""

    def __init__(self, app):
        super().__init__(app)
        limiter_kwargs = {
            "capacity": settings.rate_limit_burst,
            "refill_per_sec": settings.rate_limit_rps,
        }

        if RedisBucketLimiter is None:
            reason = _redis_import_error or "redis client not available"
            logger.warning(
                "Redis rate limiter unavailable (%s); falling back to in-memory limiter.",
                reason,
            )
            self.limiter = InMemoryBucketLimiter(**limiter_kwargs)
            return

        try:
            self.limiter = RedisBucketLimiter(**limiter_kwargs)
        except Exception as exc:
            logger.warning(
                "Redis rate limiter unavailable (%s); falling back to in-memory limiter.",
                exc,
            )
            self.limiter = InMemoryBucketLimiter(**limiter_kwargs)

    async def dispatch(self, request: Request, call_next):
        if self.limiter and request.url.path.startswith(settings.api_prefix):
            token = request.headers.get("X-API-Key")
            if not token and request.client:
                token = request.client.host
            if token and not self.limiter.allow(token):
                return Response(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
        return await call_next(request)
