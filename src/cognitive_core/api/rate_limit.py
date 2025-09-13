from __future__ import annotations

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from ..config import settings
from ..rate_limiter import RedisBucketLimiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware enforcing simple token-bucket rate limits using Redis."""

    def __init__(self, app):
        super().__init__(app)
        try:
            self.limiter = RedisBucketLimiter(
                capacity=settings.rate_limit_burst,
                refill_per_sec=settings.rate_limit_rps,
            )
        except Exception:
            self.limiter = None

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
