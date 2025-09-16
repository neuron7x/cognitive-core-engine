from __future__ import annotations

from typing import Iterable

from cognitive_core.core.math_utils import dot as _dot
from cognitive_core.core.math_utils import solve_2x2 as _solve_2x2


def dot(a: Iterable[float], b: Iterable[float]) -> float:
    a_list = list(a)
    b_list = list(b)
    if len(a_list) != len(b_list):
        raise ValueError("Vectors must be the same length")
    return float(_dot(a_list, b_list))


def solve_linear_2x2(
    a11: float, a12: float, a21: float, a22: float, b1: float, b2: float
) -> tuple[float, float]:
    x, y = _solve_2x2(a11, a12, a21, a22, b1, b2)
    return float(x), float(y)
