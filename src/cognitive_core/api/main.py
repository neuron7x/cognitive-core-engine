from fastapi import FastAPI

from ..config.settings import Settings
from .routers import events, health, math, pipelines

settings = Settings()
app = FastAPI(title=settings.app_name)
# Register application routers
app.include_router(health.router, prefix=settings.api_prefix, tags=["health"])
app.include_router(math.router, prefix=settings.api_prefix, tags=["math"])
app.include_router(events.router, prefix=settings.api_prefix, tags=["events"])
app.include_router(pipelines.router, prefix=settings.api_prefix, tags=["pipelines"])


@app.get("/")
def root():
    """Return basic application information."""
    return {"name": settings.app_name}
