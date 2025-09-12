from __future__ import annotations
from typing import Iterable

def dot(a: Iterable[float], b: Iterable[float]) -> float:
    a_list = list(a); b_list = list(b)
    if len(a_list) != len(b_list):
        raise ValueError("Vectors must be the same length")
    return float(sum(x*y for x,y in zip(a_list,b_list)))

def solve_linear_2x2(a11: float, a12: float, a21: float, a22: float, b1: float, b2: float) -> tuple[float, float]:
    det = a11*a22 - a12*a21
    if det == 0:
        raise ValueError("Singular matrix")
    x = (b1*a22 - b2*a12) / det
    y = (a11*b2 - a21*b1) / det
    return float(x), float(y)
