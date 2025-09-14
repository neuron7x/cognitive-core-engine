"""Authentication helpers for API endpoints."""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from ..config import settings

# Header name that clients must supply API keys in.
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str | None = Security(api_key_header)) -> None:
    """Validate the provided API key against configured settings.

    If ``settings.api_key`` is not configured, authentication is effectively
    disabled and all requests are allowed.  When configured, requests must
    include the correct key in the ``X-API-Key`` header or a ``403`` is raised.
    """
    # Build list of valid keys. Prefer `api_keys` when provided; fall back to a
    # single `api_key`.  An empty string counts as a configured key and will
    # require an exact match from the client.
    valid = settings.api_keys or ([] if settings.api_key is None else [settings.api_key])
    if not valid:
        return
    if api_key not in valid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")
