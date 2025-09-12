"""
Mathematical utilities: log-sum-exp, stable softmax, Welford variance.

All functions include rigorous numerics and complexity notes.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np


def logsumexp(x: np.ndarray) -> float:
    r"""
    Compute the numerically stable log-sum-exp:
    $$
    \operatorname{LSE}(x) := \log\!\Big(\sum_{i=1}^n e^{x_i}\Big)
    = m + \log\!\Big(\sum_{i=1}^n e^{x_i - m}\Big),
    \quad m = \max_i x_i.
    $$

    **Foundation:** numerical analysis; stability via max-shift (avoid overflow/underflow).
    **Error bound (float64):** relative error $\le O(n \cdot \epsilon_{mach})$ for
    well-scaled inputs where $e^{x_i-m}\in[0,1]$ (Higham, *Accuracy and Stability*, 2002).

    Preconditions:
      - x is 1-D and finite.

    Postconditions:
      - Returns finite `float`.

    Complexity:
      - Time: $O(n)$, Space: $O(1)$ (ignoring input storage).
    """
    x = np.asarray(x, dtype=np.float64).ravel()
    if x.size == 0:
        return float("-inf")
    m = float(np.max(x))
    y = np.exp(x - m)  # in [0, ∞), safe due to shift
    s = float(np.sum(y))
    return m + np.log(s)


def stable_softmax(x: np.ndarray) -> np.ndarray:
    r"""
    Compute the softmax with log-sum-exp stabilization:
    $$
    \sigma(x)_i = \frac{e^{x_i}}{\sum_j e^{x_j}}
    = \frac{e^{x_i-m}}{\sum_j e^{x_j-m}}, \quad m=\max_j x_j.
    $$

    Properties:
      - Invariance: $\sigma(x + c\mathbf{1}) = \sigma(x)$.
      - Sum-to-one: $\sum_i \sigma(x)_i = 1$ up to rounding.

    Preconditions: finite 1-D `x`.
    Postconditions: probabilities in $(0,1)$ summing to ~1.

    Complexity: $O(n)$ time, $O(1)$ extra space.
    """
    x = np.asarray(x, dtype=np.float64).ravel()
    if x.size == 0:
        return np.array([], dtype=np.float64)
    m = float(np.max(x))
    y = np.exp(x - m)
    denom = float(np.sum(y))
    return y / denom


def welford_variance(stream: Iterable[float]) -> tuple[float, float]:
    r"""
    Online mean/variance via Welford (1962):
    For samples $x_k$,
    $$
    \mu_k = \mu_{k-1} + \frac{x_k-\mu_{k-1}}{k},\quad
    M_k = M_{k-1} + (x_k-\mu_{k-1})(x_k-\mu_k).
    $$
    Unbiased variance: $s^2 = M_n / (n-1)$ for $n\ge 2$.

    **Foundation:** numerically stable single-pass variance (Knuth TAOCP 2).

    Returns:
      (mean, variance_unbiased)

    Preconditions:
      - Finite inputs; at least one element for mean; ≥2 for variance.

    Complexity: $O(n)$ time, $O(1)$ space.
    """
    n = 0
    mean = 0.0
    M2 = 0.0
    for x in stream:
        n += 1
        dx = x - mean
        mean += dx / n
        M2 += dx * (x - mean)
    if n == 0:
        return (float("nan"), float("nan"))
    var = M2 / (n - 1) if n > 1 else float("nan")
    return (mean, var)
