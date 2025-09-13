"""UMAA+EPAUP metrics package."""
from .registry import register_metric, get, list_metrics

# Import evaluators so they register themselves
from .evaluators import (
    role_adherence,  # noqa: F401
    reasoning_soundness,  # noqa: F401
    ethical_compliance,  # noqa: F401
    hallucination_risk,  # noqa: F401
    stability,  # noqa: F401
)

__all__ = ["register_metric", "get", "list_metrics"]
