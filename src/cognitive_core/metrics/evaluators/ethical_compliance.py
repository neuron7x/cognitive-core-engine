"""Ethical compliance metric stub."""
from typing import Any, Dict
from ..registry import register_metric


@register_metric("ethical_compliance")
def evaluate(task: Dict[str, Any]) -> Dict[str, float]:
    """Dummy ethical compliance evaluation."""
    return {"score": 1.0}
