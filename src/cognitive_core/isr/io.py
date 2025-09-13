"""Input/output helpers for ISR simulations."""
from __future__ import annotations
import numpy as np
import yaml


def save_npz(path: str, theta: np.ndarray) -> None:
    """Save simulation results to NPZ."""
    np.savez_compressed(path, theta=theta)


def load_npz(path: str) -> np.ndarray:
    """Load simulation results from NPZ."""
    data = np.load(path)
    return data["theta"]


def save_metadata(path: str, meta: dict) -> None:
    """Write YAML metadata."""
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(meta, f)
