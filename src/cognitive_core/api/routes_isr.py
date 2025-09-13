"""Routes for ISR simulations."""
from __future__ import annotations
from fastapi import APIRouter

router = APIRouter(prefix="/v1/isr", tags=["isr"])


@router.get("/health")
async def health() -> dict:
    """Basic ISR health endpoint."""
    return {"status": "ok"}
