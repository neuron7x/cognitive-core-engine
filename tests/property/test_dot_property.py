import importlib

import pytest

hypothesis = pytest.importorskip("hypothesis")
given = hypothesis.given
st = hypothesis.strategies

math_utils = importlib.import_module("cognitive_core.core.math_utils")
dot = math_utils.dot


@given(
    st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=64),
    st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=64),
)
def test_comm(a, b):
    n = min(len(a), len(b))
    assert dot(a[:n], b[:n]) == dot(b[:n], a[:n])
