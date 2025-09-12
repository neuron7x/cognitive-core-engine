from fastapi import APIRouter
from pydantic import BaseModel
from ...app.services import dot, solve_linear_2x2

class DotReq(BaseModel):
    a: list[float]
    b: list[float]

class Solve2x2Req(BaseModel):
    a11: float; a12: float; a21: float; a22: float; b1: float; b2: float

router = APIRouter()

@router.post("/dot")
def dot_endpoint(req: DotReq):
    return {"result": dot(req.a, req.b)}

@router.post("/solve2x2")
def solve2x2(req: Solve2x2Req):
    x,y = solve_linear_2x2(req.a11, req.a12, req.a21, req.a22, req.b1, req.b2)
    return {"x": x, "y": y}
