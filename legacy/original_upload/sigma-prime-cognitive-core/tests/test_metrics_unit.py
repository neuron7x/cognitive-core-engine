import math

import numpy as np

from tools.sigma_prime.metrics import (
    compute_epsilon,
    compute_phi,
    compute_psi,
    compute_sigma_prime,
    compute_tau,
)


def test_phi_basic_and_edge():
    A = np.array([[1, 2], [3, 4]], dtype=float)
    phi = compute_phi(A)
    assert phi > 0
    # zero matrix => denom=0 => phi=0
    Z = np.zeros((2, 2))
    assert compute_phi(Z) == 0.0


def test_phi_non_square_raises():
    import pytest

    with pytest.raises(ValueError):
        compute_phi(np.ones((2, 3)))


def test_psi_bounds():
    assert compute_psi(-5) == 0.0
    assert compute_psi(0) == 0.0
    assert 0.0 < compute_psi(50) < 1.0
    assert compute_psi(1000) == 1.0


def test_epsilon_bounds():
    assert compute_epsilon(-2) == 1.0
    assert compute_epsilon(0.25) == 0.25


def test_tau_vector_and_nan_guard():
    a = dict(hours_ai=1, hours_training=2, hours_motorcycle=3, hours_dog=4)
    b = dict(hours_ai=1, hours_training=2, hours_motorcycle=3, hours_dog=4)
    t = compute_tau(a, b)
    assert math.isclose(t, 1.0, rel_tol=1e-6) or t == 1.0
    # zero variance => 0.0
    z = dict(hours_ai=1, hours_training=1, hours_motorcycle=1, hours_dog=1)
    assert compute_tau(z, z) == 0.0


def test_sigma_prime_non_negative_and_value():
    phi, psi, eps, tau = 0.5, 0.8, 0.3, 0.7
    val = compute_sigma_prime(phi, psi, eps, tau, 0.2, 0.3, 0.4)
    assert val >= 0.0
    # negative raises
    import pytest

    with pytest.raises(ValueError):
        compute_sigma_prime(-1, 0, 0, 0, 0, 0, 0)
