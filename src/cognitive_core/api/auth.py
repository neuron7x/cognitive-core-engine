"""Authentication helpers for API endpoints."""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from ..config import settings
from ..utils.telemetry import Counter

# Header name that clients must supply API keys in.
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Counter for failed authentication attempts
API_KEY_FAILURES = Counter("api_key_auth_failures_total", "Invalid API key attempts")


async def verify_api_key(api_key: str | None = Security(api_key_header)) -> None:
    """Validate the provided API key against configured settings.

    Authentication is disabled when ``settings.api_keys`` is ``None`` so all
    requests are allowed. When configured, requests must include one of the
    configured keys in the ``X-API-Key`` header or a ``403`` is raised.
    """
    if settings.api_keys is None:
        return

    if api_key is None or api_key not in settings.api_keys:
        API_KEY_FAILURES.inc()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")
