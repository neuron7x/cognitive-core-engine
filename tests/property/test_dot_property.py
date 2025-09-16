import pytest

try:  # pragma: no cover - optional dependency
    from hypothesis import given, strategies as st
except ModuleNotFoundError:  # pragma: no cover - skip if hypothesis unavailable
    pytest.skip("hypothesis is not installed", allow_module_level=True)

from cognitive_core.core.math_utils import dot


@given(
    st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=64),
    st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=64),
)
def test_comm(a, b):
    n = min(len(a), len(b))
    assert dot(a[:n], b[:n]) == dot(b[:n], a[:n])
