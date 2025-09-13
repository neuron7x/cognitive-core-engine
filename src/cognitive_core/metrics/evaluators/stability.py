"""Stability metric stub."""
from typing import Any, Dict
from ..registry import register_metric


@register_metric("stability")
def evaluate(task: Dict[str, Any]) -> Dict[str, float]:
    """Dummy stability evaluation."""
    return {"score": 1.0}
