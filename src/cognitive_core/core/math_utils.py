from typing import Iterable, Tuple
def dot(a: Iterable[float], b: Iterable[float]) -> float:
    s = 0.0
    for x, y in zip(a, b):
        s += float(x) * float(y)
    return s
def solve_2x2(a: float, b: float, c: float, d: float, e: float, f: float) -> Tuple[float, float]:
    det = a*d - b*c
    if det == 0:
        raise ValueError("Singular matrix")
    x = (e*d - b*f) / det
    y = (a*f - e*c) / det
    return (x, y)
