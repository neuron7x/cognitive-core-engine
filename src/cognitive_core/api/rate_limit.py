from __future__ import annotations

import heapq
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
        self._state: dict[str, tuple[float, float, float]] = {}
        self._expirations: list[tuple[float, str]] = []
        self._lock = threading.Lock()

    def _prune_expired(self, now: float) -> None:
        if not self._expirations:
            return

        while self._expirations and self._expirations[0][0] <= now:
            _, token = heapq.heappop(self._expirations)
            state = self._state.get(token)
            if not state:
                continue

            _, _, expiry = state
            if expiry <= now:
                self._state.pop(token, None)

    def allow(self, token: str, needed: float = 1.0) -> bool:
        now = time.time()
        with self._lock:
            self._prune_expired(now)

            tokens, last_ts, _ = self._state.get(token, (self.capacity, now, now))
            tokens = min(self.capacity, tokens + (now - last_ts) * self.refill_per_sec)
            allowed = tokens >= needed
            if allowed:
                tokens -= needed
            if tokens >= self.capacity:
                self._state.pop(token, None)
            else:
                if self.refill_per_sec > 0:
                    expiry = now + (self.capacity - tokens) / self.refill_per_sec
                    self._state[token] = (tokens, now, expiry)
                    heapq.heappush(self._expirations, (expiry, token))
                else:
                    # When no refill is configured we cannot compute a meaningful
                    # expiry, so keep the latest state without scheduling cleanup.
                    self._state[token] = (tokens, now, float("inf"))
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
        if (
            self.limiter
            and request.url.path.startswith(settings.api_prefix)
        ):
            token = request.headers.get("X-API-Key")
            if not token and request.client:
                token = request.client.host
            if token and not self.limiter.allow(token):
                return Response(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
        return await call_next(request)
