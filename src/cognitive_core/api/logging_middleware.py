from __future__ import annotations

import logging
import time
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log request/response details including request id and token count."""

    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("cognitive_core.request")

    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or str(uuid4())
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        token_count = int(response.headers.get("X-Token-Count", "0"))
        self.logger.info(
            "%s %s status=%s request_id=%s tokens=%s latency=%.3f",
            request.method,
            request.url.path,
            response.status_code,
            req_id,
            token_count,
            duration,
        )
        response.headers["X-Request-ID"] = req_id
        return response
