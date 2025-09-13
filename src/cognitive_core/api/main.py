from fastapi import FastAPI
from fastapi.responses import Response

from ..config.settings import Settings
from ..utils.telemetry import setup_telemetry
try:  # pragma: no cover - allow running without prometheus-client installed
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
except Exception:  # pragma: no cover - fallback
    CONTENT_TYPE_LATEST = "text/plain"
    def generate_latest() -> bytes:  # type: ignore
        return b""
from .routers import events, health, math, pipelines

settings = Settings()
setup_telemetry(settings.app_name)
app = FastAPI(title=settings.app_name)
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
