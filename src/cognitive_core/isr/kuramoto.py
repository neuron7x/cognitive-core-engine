"""Kuramoto model simulation utilities."""
from __future__ import annotations
import numpy as np


def simulate(theta0: np.ndarray, omega: np.ndarray, A: np.ndarray, K: float = 1.0, dt: float = 0.01, tmax: float = 10.0) -> np.ndarray:
    """Simulate coupled oscillators using a simple Euler integrator."""
    n = len(theta0)
    steps = int(tmax / dt)
    theta = np.empty((steps, n))
    theta[0] = theta0
    for t in range(1, steps):
        coupling = np.sum(A * np.sin(theta[t - 1] - theta[t - 1][:, None]), axis=1)
        dtheta = omega + (K / n) * coupling
        theta[t] = (theta[t - 1] + dt * dtheta) % (2 * np.pi)
    return theta
