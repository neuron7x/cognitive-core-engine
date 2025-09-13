"""Spectral analysis utilities for ISR."""
from __future__ import annotations
import numpy as np


def order_parameter(theta: np.ndarray) -> np.ndarray:
    """Compute Kuramoto order parameter over time."""
    return np.abs(np.mean(np.exp(1j * theta), axis=1))


def laplacian_spectrum(A: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return eigenvalues and eigenvectors of graph Laplacian."""
    D = np.diag(A.sum(axis=1))
    L = D - A
    return np.linalg.eigh(L)
