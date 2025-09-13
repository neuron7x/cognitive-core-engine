"""Routes for metric evaluation."""
from __future__ import annotations
from fastapi import APIRouter
from ..metrics import registry

router = APIRouter(prefix="/v1/metrics", tags=["metrics"])


@router.get("/list")
async def list_metrics() -> dict:
    """Return available metric names."""
    return {"metrics": registry.list_metrics()}
