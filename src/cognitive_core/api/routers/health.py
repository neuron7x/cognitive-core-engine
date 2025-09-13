"""Basic health and service information endpoints."""

from importlib.metadata import PackageNotFoundError, version

from fastapi import APIRouter

from ...utils.telemetry import instrument_route

from ...config import settings

router = APIRouter()


@router.get("/health")
@router.get("/healthz")
@instrument_route("health")
def health() -> dict[str, str]:
    """Return a basic health status."""
    return {"status": "ok"}


@router.get("/livez")
@instrument_route("live")
def live() -> dict[str, str]:
    """Simple liveness probe."""
    return {"status": "ok"}


@router.get("/readyz")
@instrument_route("ready")
def ready() -> dict[str, str]:
    """Readiness probe with a trivial dependency check."""
    dependencies_ok = bool(settings.app_name)
    return {"status": "ok" if dependencies_ok else "fail"}


@router.get("/v1/info")
@instrument_route("info")
def info() -> dict[str, str]:
    """Return application metadata."""
    try:
        app_version = version("cognitive-core-engine")
    except PackageNotFoundError:  # pragma: no cover - fallback when package isn't installed
        app_version = "unknown"
    return {"name": settings.app_name, "version": app_version}
