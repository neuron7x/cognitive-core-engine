import numpy as np
from hypothesis import given, strategies as st
from tools.algorithms.math_utils import logsumexp, stable_softmax, welford_variance

@given(st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False), min_size=1, max_size=64))
def test_logsumexp_monotone(xs):
    a = np.array(xs, dtype=np.float64)
    l1 = logsumexp(a)
    l2 = logsumexp(a + 1.0)
    assert l2 > l1  # adding constant increases LSE by exactly that constant
    assert np.isfinite(l1) and np.isfinite(l2)

@given(st.lists(st.floats(min_value=-50, max_value=50, allow_nan=False, allow_infinity=False), min_size=1, max_size=64))
def test_softmax_properties(xs):
    x = np.array(xs, dtype=np.float64)
    p = stable_softmax(x)
    assert np.all(p >= 0) and np.all(p <= 1)
    s = float(np.sum(p))
    assert np.isclose(s, 1.0, atol=1e-9)
    p_shift = stable_softmax(x + 7.0)
    assert np.allclose(p, p_shift, atol=1e-12)

def test_welford_matches_numpy():
    rng = np.random.default_rng(42)
    x = rng.normal(size=1000)
    m, v = welford_variance(x.tolist())
    assert np.isclose(m, np.mean(x), atol=1e-10)
    assert np.isclose(v, np.var(x, ddof=1), rtol=1e-6)

def test_derivative_identity_sympy():
    import sympy as sp
    x1, x2 = sp.symbols('x1 x2', real=True)
    x = sp.Matrix([x1, x2])
    lse = sp.log(sp.exp(x1) + sp.exp(x2))
    # gradient of LSE equals softmax
    g = sp.Matrix([sp.diff(lse, x1), sp.diff(lse, x2)])
    s = sp.Matrix([sp.exp(x1)/(sp.exp(x1)+sp.exp(x2)), sp.exp(x2)/(sp.exp(x1)+sp.exp(x2))])
    assert sp.simplify(g - s) == sp.Matrix([0,0])
