import time
from typing import Any

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .core.math_utils import dot, solve_2x2


class DotRequest(BaseModel):
    a: list[float]
    b: list[float]


class DotResponse(BaseModel):
    dot: float


class Solve2x2Request(BaseModel):
    a: float
    b: float
    c: float
    d: float
    e: float
    f: float


class Solve2x2Response(BaseModel):
    x: float
    y: float


app = FastAPI(title="cognitive-core-engine")


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "name": "cognitive-core-engine"}


@app.post("/api/dot", response_model=DotResponse)
def dot_api(req: DotRequest) -> DotResponse:
    n = min(len(req.a), len(req.b))
    return DotResponse(dot=dot(req.a[:n], req.b[:n]))


@app.post("/api/solve2x2", response_model=Solve2x2Response)
def solve2x2_api(req: Solve2x2Request) -> Solve2x2Response:
    x, y = solve_2x2(req.a, req.b, req.c, req.d, req.e, req.f)
    return Solve2x2Response(x=x, y=y)


def _sse_gen():
    for i in range(3):
        yield f"data: ping {i}\n\n"
        time.sleep(0.05)


@app.get("/api/events/sse")
def events_sse():
    return StreamingResponse(_sse_gen(), media_type="text/event-stream")
