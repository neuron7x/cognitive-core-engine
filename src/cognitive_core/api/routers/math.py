from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...app.services import dot, solve_linear_2x2
from ...utils.telemetry import instrument_route


class DotReq(BaseModel):
    a: list[float]
    b: list[float]


class Solve2x2Req(BaseModel):
    a: float
    b: float
    c: float
    d: float
    e: float
    f: float


router = APIRouter()


@router.post("/dot")
@instrument_route("dot")
def dot_endpoint(req: DotReq):
    return {"result": dot(req.a, req.b)}


@router.post("/solve2x2")
@instrument_route("solve2x2")
def solve2x2(req: Solve2x2Req):
    try:
        x, y = solve_linear_2x2(req.a, req.b, req.c, req.d, req.e, req.f)
    except ValueError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"x": x, "y": y}
