"""Authentication helpers for API endpoints."""

import hmac
import logging

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from ..config import settings

logger = logging.getLogger(__name__)

# Header name that clients must supply API keys in.
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str | None = Security(api_key_header)) -> None:
    """Validate the provided API key against configured settings.

    The API key must be configured through ``COG_API_KEY`` (supporting multiple
    comma-separated values). If no usable key is present, the service treats
    this as a deployment error and returns ``500``. Otherwise, the provided
    header must match one of the configured keys or a ``403`` is raised.
    """
    configured_key = settings.api_key
    if not isinstance(configured_key, str):
        configured_key = getattr(configured_key, "default", configured_key)

    if configured_key is None or not configured_key.strip():
        logger.critical(
            "API key is not configured. Set the COG_API_KEY environment variable "
            "before accepting requests.",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key is not configured",
        )

    valid_keys = [k.strip() for k in configured_key.split(",") if k.strip()]
    if not valid_keys:
        logger.critical(
            "API key configuration did not yield any usable keys. Check COG_API_KEY.",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key configuration invalid",
        )

    provided_key = api_key or ""
    for valid_key in valid_keys:
        if hmac.compare_digest(valid_key, provided_key):
            break
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")
