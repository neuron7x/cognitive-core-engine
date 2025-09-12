import numpy as np
import pytest
from hypothesis import given, strategies as st
from tools.sigma_prime.metrics import compute_phi

@given(st.integers(min_value=1, max_value=8))
def test_phi_non_negative(n):
    # random square matrix
    A = np.random.randn(n, n)
    val = compute_phi(A)
    assert val >= 0.0

@given(st.integers(min_value=1, max_value=6))
def test_phi_zero_matrix(n):
    import numpy as np
    Z = np.zeros((n,n))
    assert compute_phi(Z) == 0.0
