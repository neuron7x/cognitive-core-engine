"""Middleware wiring guard checks into the API."""
from __future__ import annotations
from fastapi import Request, Response


async def guard_middleware(request: Request, call_next) -> Response:  # type: ignore[override]
    """Dummy guard middleware that currently passes through requests."""
    response = await call_next(request)
    response.headers.setdefault("X-Guard-Report", "allow")
    return response
