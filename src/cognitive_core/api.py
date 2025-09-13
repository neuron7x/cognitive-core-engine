import time
from typing import Any, Dict, Iterable

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from .core.math_utils import dot
from .app import services

app = FastAPI(title="cognitive-core-engine")


@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "name": "cognitive-core-engine"}


@app.post("/api/dot")
def dot_api(payload: Dict[str, Iterable[float]]):
    a = payload.get("a", [])
    b = payload.get("b", [])
    n = min(len(a), len(b))
    return {"dot": dot(a[:n], b[:n])}


_SOLVE2X2_PARAM_MAP = {
    "a11": "a",
    "a12": "b",
    "a21": "c",
    "a22": "d",
    "b1": "e",
    "b2": "f",
}


@app.post("/api/solve2x2")
def solve2x2_api(payload: Dict[str, float]):
    params: Dict[str, float] = {}
    for new_key, old_key in _SOLVE2X2_PARAM_MAP.items():
        if new_key in payload:
            params[new_key] = payload[new_key]
        elif old_key in payload:
            params[new_key] = payload[old_key]
        else:
            raise KeyError(f"Missing '{new_key}' or '{old_key}'")
    x, y = services.solve_linear_2x2(**params)
    return {"x": x, "y": y}


def _sse_gen():
    for i in range(3):
        yield f"data: ping {i}\n\n"
        time.sleep(0.05)


@app.get("/api/events/sse")
def events_sse():
    return StreamingResponse(_sse_gen(), media_type="text/event-stream")
