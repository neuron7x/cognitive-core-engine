from fastapi import FastAPI

from ..config.settings import Settings
from .routers import events, health, math, pipelines
from .middleware_guards import guard_middleware

try:  # Optional routes
    from .routes_metrics import router as metrics_router
except Exception:  # pragma: no cover - missing optional deps
    metrics_router = None

try:
    from .routes_isr import router as isr_router
except Exception:  # pragma: no cover - missing optional deps
    isr_router = None

settings = Settings()
app = FastAPI(title=settings.app_name)
app.middleware("http")(guard_middleware)

# Register application routers
app.include_router(health.router, prefix=settings.api_prefix, tags=["health"])
app.include_router(math.router, prefix=settings.api_prefix, tags=["math"])
app.include_router(events.router, prefix=settings.api_prefix, tags=["events"])
app.include_router(pipelines.router, prefix=settings.api_prefix, tags=["pipelines"])
if metrics_router:
    app.include_router(metrics_router)
if isr_router:
    app.include_router(isr_router)


@app.get("/")
def root():
    """Return basic application information."""
    return {"name": settings.app_name}
