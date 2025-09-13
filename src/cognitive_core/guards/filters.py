"""Simple request filters for guard checks."""
from __future__ import annotations
from typing import Dict, Any


def categorize(request: Dict[str, Any]) -> str:
    """Return a dummy category for a request."""
    return "allow"
