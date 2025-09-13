"""Role adherence metric stub."""
from typing import Any, Dict
from . import __init__ as _  # to satisfy flake
from ..registry import register_metric


@register_metric("role_adherence")
def evaluate(task: Dict[str, Any]) -> Dict[str, float]:
    """Dummy role adherence evaluation."""
    return {"score": 1.0}
