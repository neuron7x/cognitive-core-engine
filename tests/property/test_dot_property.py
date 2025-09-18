import pytest

try:  # pragma: no cover - optional dependency
    from hypothesis import given, strategies as st
except ModuleNotFoundError:  # pragma: no cover - skip if hypothesis unavailable
    pytest.skip("hypothesis is not installed", allow_module_level=True)

from cognitive_core.core.math_utils import dot


float_values = st.floats(
    min_value=-1e6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
)


@given(
    st.integers(min_value=1, max_value=64).flatmap(
        lambda length: st.tuples(
            st.lists(
                float_values,
                min_size=length,
                max_size=length,
            ),
            st.lists(
                float_values,
                min_size=length,
                max_size=length,
            ),
        )
    )
)
def test_comm(values):
    a, b = values
    assert dot(a, b) == dot(b, a)
