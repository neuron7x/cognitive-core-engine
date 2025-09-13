"""Policy application utilities."""
from __future__ import annotations
from typing import Dict, Any
import yaml


def load_policies(path: str) -> Dict[str, Any]:
    """Load guard policies from YAML."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
