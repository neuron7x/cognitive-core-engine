from hypothesis import given, strategies as st
from cognitive_core.core.math_utils import dot
@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=64),
       st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=64))
def test_comm(a,b):
    n=min(len(a),len(b)); assert dot(a[:n],b[:n])==dot(b[:n],a[:n])
