"""Reasoning soundness metric stub."""
from typing import Any, Dict
from ..registry import register_metric


@register_metric("reasoning_soundness")
def evaluate(task: Dict[str, Any]) -> Dict[str, float]:
    """Dummy reasoning soundness evaluation."""
    return {"score": 1.0}
