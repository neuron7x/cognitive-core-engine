from __future__ import annotations
from typing import Protocol

class Plugin(Protocol):
    name: str
    def run(self, payload: dict) -> dict: ...

REGISTRY: dict[str, Plugin] = {}

def register(plugin: Plugin) -> None:
    REGISTRY[plugin.name] = plugin

def dispatch(name: str, payload: dict) -> dict:
    p = REGISTRY.get(name)
    if not p:
        raise KeyError(f"Plugin '{name}' not found")
    return p.run(payload)
