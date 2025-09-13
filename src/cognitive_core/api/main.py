from fastapi import FastAPI

from .health import router as health_router
from .routers import math
from ..infra import metrics

app = FastAPI(title="Cognitive Core Engine")
app.include_router(health_router)
app.include_router(math.router, prefix="/api")
app.include_router(metrics.router)
