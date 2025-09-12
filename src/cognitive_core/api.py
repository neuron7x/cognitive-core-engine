from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Iterable
import time
from .core.math_utils import dot, solve_2x2
app = FastAPI(title="cognitive-core-engine")
@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "name": "cognitive-core-engine"}
@app.post("/api/dot")
def dot_api(payload: Dict[str, Iterable[float]]):
    a = payload.get("a", []); b = payload.get("b", [])
    n = min(len(a), len(b))
    return {"dot": dot(a[:n], b[:n])}
@app.post("/api/solve2x2")
def solve2x2_api(payload: Dict[str, float]):
    x, y = solve_2x2(payload["a"], payload["b"], payload["c"], payload["d"], payload["e"], payload["f"])
    return {"x": x, "y": y}
def _sse_gen():
    for i in range(3):
        yield f"data: ping {i}\n\n"; time.sleep(0.05)
@app.get("/api/events/sse")
def events_sse():
    return StreamingResponse(_sse_gen(), media_type="text/event-stream")
