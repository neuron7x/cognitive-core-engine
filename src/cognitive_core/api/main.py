from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from ..config import settings
from ..utils.telemetry import setup_telemetry
from .auth import verify_api_key
from .rate_limit import RateLimitMiddleware
from .security import SecureHeadersMiddleware
try:  # pragma: no cover - allow running without prometheus-client installed
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
except Exception:  # pragma: no cover - fallback
    CONTENT_TYPE_LATEST = "text/plain"
    def generate_latest() -> bytes:  # type: ignore
        return b""
from .routers import events, health, math, pipelines

setup_telemetry(settings.app_name, enable_console_export=settings.telemetry_console_export)
app = FastAPI(title=settings.app_name, dependencies=[Depends(verify_api_key)])
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    SecureHeadersMiddleware,
    referrer_policy=settings.security_referrer_policy,
    permissions_policy=settings.security_permissions_policy,
    content_security_policy=settings.security_content_security_policy,
)
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
