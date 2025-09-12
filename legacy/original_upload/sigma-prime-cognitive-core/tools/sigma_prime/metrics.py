"""
Sigma-Prime metrics — operational definitions for cognitive state dynamics.
Implements Φ, Ψ, Ε, Τ and Σ'(t) with safe guards.
"""
from __future__ import annotations
from typing import Sequence
import numpy as np

def compute_phi(network_matrix: np.ndarray) -> float:
    """
    Φ = sum(|λ_i|) / sum(|w_ij|), where λ_i are eigenvalues of a square matrix.
    Returns 0.0 if weight sum == 0.
    Raises ValueError if matrix is not square.
    """
    A = np.asarray(network_matrix, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("network_matrix must be square")
    if A.size == 0:
        return 0.0
    # eigenvalues can be complex; use magnitude
    eig = np.linalg.eigvals(A)
    num = float(np.sum(np.abs(eig)))
    denom = float(np.sum(np.abs(A)))
    return 0.0 if denom == 0.0 else num / denom

def compute_psi(query_count: int) -> float:
    """
    Ψ = min(query_count / 100, 1). Negative counts are clamped at 0.
    """
    qc = max(0, int(query_count))
    return min(qc / 100.0, 1.0)

def compute_epsilon(emotion_intensity: float) -> float:
    """
    Ε = min(|emotion_intensity|, 1)
    """
    return min(abs(float(emotion_intensity)), 1.0)

def compute_tau(activity_t: dict, activity_t_minus_1: dict) -> float:
    """
    Τ = Pearson correlation between activity vectors at t and t-1.
    Keys required: hours_ai, hours_training, hours_motorcycle, hours_dog.
    If correlation is NaN (e.g., zero variance), returns 0.0.
    """
    keys = ["hours_ai", "hours_training", "hours_motorcycle", "hours_dog"]
    try:
        x = np.array([float(activity_t[k]) for k in keys], dtype=float)
        y = np.array([float(activity_t_minus_1[k]) for k in keys], dtype=float)
    except KeyError as e:
        raise KeyError(f"Missing key in activities: {e}")
    # Handle zero variance => corr undefined → 0.0
    if np.allclose(np.std(x), 0.0) or np.allclose(np.std(y), 0.0):
        return 0.0
    # Pearson correlation
    corr = float(np.corrcoef(x, y)[0, 1])
    if np.isnan(corr):
        return 0.0
    return corr

def compute_sigma_prime(phi: float, psi: float, epsilon: float, tau: float,
                        eta: float, alpha: float, recurrence: float) -> float:
    """
    Σ'(t) = (phi^0.8 * psi^0.7 * epsilon^0.5 * tau^0.4) * H(eta, alpha, recurrence)
    H = 3*eta*alpha*recurrence / (eta + alpha + recurrence + 1e-8)
    All inputs must be >= 0, otherwise ValueError.
    """
    vals = [phi, psi, epsilon, tau, eta, alpha, recurrence]
    if any(v < 0 for v in vals):
        raise ValueError("All inputs must be non-negative")
    # Exponents
    ae, be, ge, de = 0.8, 0.7, 0.5, 0.4
    harmonic = (3.0 * eta * alpha * recurrence) / (eta + alpha + recurrence + 1e-8)
    return (phi**ae) * (psi**be) * (epsilon**ge) * (tau**de) * harmonic
