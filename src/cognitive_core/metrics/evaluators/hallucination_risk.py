"""Hallucination risk metric stub."""
from typing import Any, Dict
from ..registry import register_metric


@register_metric("hallucination_risk")
def evaluate(task: Dict[str, Any]) -> Dict[str, float]:
    """Dummy hallucination risk evaluation."""
    return {"score": 1.0}
