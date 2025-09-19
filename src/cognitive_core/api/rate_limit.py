from __future__ import annotations

import heapq
import logging
import threading
import time

import ipaddress

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from uvicorn.middleware.proxy_headers import _parse_raw_hosts

from ..config import settings

_redis_import_error: Exception | None = None

try:
    from ..rate_limiter import RateLimiterUnavailableError, RedisBucketLimiter
except Exception as exc:
    RedisBucketLimiter = None  # type: ignore[assignment]
    _redis_import_error = exc
else:
    _redis_import_error = None


logger = logging.getLogger(__name__)


class InMemoryBucketLimiter:
    """Simple token bucket limiter stored in process memory."""

    NO_REFILL_TTL = 3600.0

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
                    expiry = now + self.NO_REFILL_TTL
                    self._state[token] = (tokens, now, expiry)
                    heapq.heappush(self._expirations, (expiry, token))
            return allowed


class InMemoryCostTracker:
    """Track per-client cost totals in memory."""

    def __init__(self) -> None:
        self._totals: dict[str, float] = {}
        self._lock = threading.Lock()

    def add_cost(self, key: str, amount: float) -> None:
        amount_f = float(amount)
        if amount_f == 0.0:
            return
        with self._lock:
            self._totals[key] = self._totals.get(key, 0.0) + amount_f

    def get_cost(self, key: str) -> float:
        with self._lock:
            return float(self._totals.get(key, 0.0))


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware enforcing simple token-bucket rate limits using Redis."""

    def __init__(self, app):
        super().__init__(app)
        limiter_kwargs = {
            "capacity": settings.rate_limit_burst,
            "refill_per_sec": settings.rate_limit_rps,
        }
        self._limiter_kwargs = limiter_kwargs
        self.limiter: object | None = None

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
            self._swap_to_in_memory(exc)

    def _swap_to_in_memory(self, reason: Exception | str | None = None) -> None:
        current = getattr(self, "limiter", None)
        if isinstance(current, InMemoryBucketLimiter):
            return

        if reason is not None:
            logger.warning(
                "Redis rate limiter unavailable (%s); falling back to in-memory limiter.",
                reason,
            )
        else:
            logger.warning(
                "Redis rate limiter unavailable; falling back to in-memory limiter."
            )
        self.limiter = InMemoryBucketLimiter(**self._limiter_kwargs)

    def _allow_or_fallback(self, token: str, needed: float = 1.0) -> bool:
        if not self.limiter:
            return True

        try:
            return self.limiter.allow(token, needed=needed)
        except RateLimiterUnavailableError as exc:
            self._swap_to_in_memory(exc)
            if not self.limiter:
                return True
            return self.limiter.allow(token, needed=needed)

    async def dispatch(self, request: Request, call_next):
        if (
            self.limiter
            and request.url.path.startswith(settings.api_prefix)
        ):
            client_host = self._resolve_client_host(request)
            if client_host and not self._allow_or_fallback(f"ip:{client_host}"):
                return Response(status_code=status.HTTP_429_TOO_MANY_REQUESTS)

            api_key = request.headers.get("X-API-Key")
            if api_key and not self._allow_or_fallback(f"key:{api_key}"):
                return Response(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
        return await call_next(request)

    def _resolve_client_host(self, request: Request) -> str | None:
        client_host = request.client.host if request.client else None

        if settings.trust_proxy_headers:
            header_name = settings.trusted_proxy_header
            if header_name:
                header_value = request.headers.get(header_name)
                if header_value:
                    for raw_host in _parse_raw_hosts(header_value):
                        host = raw_host.strip()
                        if not host:
                            continue
                        try:
                            ip = ipaddress.ip_address(host)
                        except ValueError:
                            continue
                        if ip.is_global:
                            return host

        return client_host
