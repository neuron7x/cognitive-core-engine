from prometheus_client import Counter, generate_latest
from fastapi import APIRouter, Response

router = APIRouter()
requests_total = Counter("requests_total", "Total HTTP requests")

@router.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain; version=0.0.4")
