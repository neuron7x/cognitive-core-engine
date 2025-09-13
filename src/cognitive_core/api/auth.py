"""Authentication helpers for API endpoints."""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from ..config import settings

# Header name that clients must supply API keys in.
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str | None = Security(api_key_header)) -> None:
    """Validate the provided API key against configured settings.

    Authentication is disabled when ``settings.api_key`` is ``None`` so all
    requests are allowed. When configured (including an empty string), requests
    must include the correct key in the ``X-API-Key`` header or a ``403`` is
    raised.
    """
    if settings.api_key is None:
        return

    if api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")
