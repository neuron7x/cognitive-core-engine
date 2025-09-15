from __future__ import annotations

from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp


CallNext = Callable[[Request], Awaitable[Response]]


class SecureHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware that adds common security headers to all responses."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        strict_transport_security: str = "max-age=63072000; includeSubDomains; preload",
        x_frame_options: str = "DENY",
        x_content_type_options: str = "nosniff",
    ) -> None:
        super().__init__(app)
        self._strict_transport_security = strict_transport_security
        self._x_frame_options = x_frame_options
        self._x_content_type_options = x_content_type_options

    async def dispatch(self, request: Request, call_next: CallNext) -> Response:
        response = await call_next(request)

        if self._strict_transport_security:
            response.headers.setdefault(
                "Strict-Transport-Security", self._strict_transport_security
            )
        if self._x_frame_options:
            response.headers.setdefault("X-Frame-Options", self._x_frame_options)
        if self._x_content_type_options:
            response.headers.setdefault(
                "X-Content-Type-Options", self._x_content_type_options
            )

        return response
