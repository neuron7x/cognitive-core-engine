from typing import List
from hypothesis import given, strategies as st

def dot(a: List[float], b: List[float]) -> float:
    return sum(x*y for x, y in zip(a, b))

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=32),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=32))
def test_dot_commutativity(a, b):
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    assert dot(a, b) == dot(b, a)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=32))
def test_dot_zero(a):
    z = [0.0]*len(a)
    assert dot(a, z) == 0.0
