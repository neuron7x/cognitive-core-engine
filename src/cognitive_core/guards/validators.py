"""Input validators for guard checks."""
from __future__ import annotations
from typing import Dict, Any


def validate_length(request: Dict[str, Any], max_chars: int = 1000) -> bool:
    """Return True if request text length is within bounds."""
    text = str(request.get("text", ""))
    return len(text) <= max_chars
