from fastapi import APIRouter
from pydantic import BaseModel

from ...core.math_utils import dot as dot_fn, solve_2x2


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


router = APIRouter()


@router.post("/dot", response_model=DotResponse)
def dot_endpoint(req: DotRequest) -> DotResponse:
    n = min(len(req.a), len(req.b))
    return DotResponse(dot=dot_fn(req.a[:n], req.b[:n]))


@router.post("/solve2x2", response_model=Solve2x2Response)
def solve2x2_endpoint(req: Solve2x2Request) -> Solve2x2Response:
    x, y = solve_2x2(req.a, req.b, req.c, req.d, req.e, req.f)
    return Solve2x2Response(x=x, y=y)
