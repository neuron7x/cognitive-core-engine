from fastapi import FastAPI

from ..config.settings import Settings
from .routers import events, health, math

settings = Settings()
app = FastAPI(title=settings.app_name)
app.include_router(health.router, prefix=settings.api_prefix, tags=["health"])
app.include_router(math.router, prefix=settings.api_prefix, tags=["math"])
app.include_router(events.router, prefix=settings.api_prefix, tags=["events"])


@app.get("/")
def root():
    return {"name": settings.app_name}
