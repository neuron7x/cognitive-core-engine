from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class Plugin(Protocol):
    """Interface that all plugins must implement."""

    def run(self, payload: dict) -> dict: ...


@dataclass
class PluginMetadata:
    """Metadata describing a plugin."""

    name: str
    version: str
    requirements: list[str]


# Maps plugin name to a tuple of (metadata, plugin instance)
REGISTRY: dict[str, tuple[PluginMetadata, Plugin]] = {}


def register(plugin: Plugin, metadata: PluginMetadata) -> None:
    """Register a plugin with associated metadata."""

    REGISTRY[metadata.name] = (metadata, plugin)


def dispatch(name: str, payload: dict) -> dict:
    """Dispatch a payload to a registered plugin."""

    entry = REGISTRY.get(name)
    if not entry:
        raise KeyError(f"Plugin '{name}' not found")
    _meta, plugin = entry
    return plugin.run(payload)
