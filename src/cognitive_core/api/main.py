from fastapi import Depends, FastAPI
from fastapi.responses import Response

from ..config import settings
from ..utils.telemetry import setup_telemetry
from .auth import verify_api_key
from .rate_limit import RateLimitMiddleware
try:  # pragma: no cover - allow running without prometheus-client installed
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
except Exception:  # pragma: no cover - fallback
    CONTENT_TYPE_LATEST = "text/plain"
    def generate_latest() -> bytes:  # type: ignore
        return b""
from .routers import events, health, math, pipelines

setup_telemetry(settings.app_name)
app = FastAPI(title=settings.app_name, dependencies=[Depends(verify_api_key)])
app.add_middleware(RateLimitMiddleware)
# Register application routers
app.include_router(health.router, prefix=settings.api_prefix, tags=["health"])
app.include_router(math.router, prefix=settings.api_prefix, tags=["math"])
app.include_router(events.router, prefix=settings.api_prefix, tags=["events"])
app.include_router(pipelines.router, prefix=settings.api_prefix, tags=["pipelines"])


@app.get("/metrics")
def metrics() -> Response:
    """Expose Prometheus metrics."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
def root():
    return {"name": settings.app_name}
