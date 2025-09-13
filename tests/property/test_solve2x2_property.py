from hypothesis import assume, given, strategies as st
import pytest

from cognitive_core.core.math_utils import solve_2x2


@given(
    st.floats(-1e6, 1e6, allow_nan=False, allow_infinity=False),
    st.floats(-1e6, 1e6, allow_nan=False, allow_infinity=False),
    st.floats(-1e6, 1e6, allow_nan=False, allow_infinity=False),
    st.floats(-1e6, 1e6, allow_nan=False, allow_infinity=False),
    st.floats(-1e6, 1e6, allow_nan=False, allow_infinity=False),
    st.floats(-1e6, 1e6, allow_nan=False, allow_infinity=False),
)
def test_recomposition(a, b, c, d, e, f):
    assume(abs(a * d - b * c) > 1e-6)
    x, y = solve_2x2(a, b, c, d, e, f)
    assert a * x + b * y == pytest.approx(e)
    assert c * x + d * y == pytest.approx(f)
