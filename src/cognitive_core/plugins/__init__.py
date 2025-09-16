from __future__ import annotations

from dataclasses import dataclass, field
from importlib.metadata import EntryPoint, entry_points
from typing import Iterable, Protocol, Sequence

from .plugin_loader import ALLOWED_PLUGINS, PluginVerificationError, load_plugin_module


class Plugin(Protocol):
    """Interface that all plugins must implement."""

    def run(self, payload: dict) -> dict: ...


@dataclass
class PluginMetadata:
    """Metadata describing a plugin."""

    name: str
    version: str
    requirements: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise PluginVerificationError("Plugin metadata name must not be empty.")

        if not self.version or not self.version.strip():
            raise PluginVerificationError("Plugin metadata version must not be empty.")

        normalized_requirements = []
        for requirement in self.requirements:
            text = str(requirement).strip()
            if text:
                normalized_requirements.append(text)

        self.requirements = tuple(normalized_requirements)


# Maps plugin name to a tuple of (metadata, plugin instance)
REGISTRY: dict[str, tuple[PluginMetadata, Plugin]] = {}


def register(plugin: Plugin, metadata: PluginMetadata) -> None:
    """Register a plugin with associated metadata."""

    existing = REGISTRY.get(metadata.name)
    if existing is not None:
        registered_meta, _registered_plugin = existing
        if registered_meta == metadata:
            # Allow idempotent registration when metadata is identical. The
            # underlying plugin may be a new instance (e.g. from entry points),
            # but integrity checks ensure it originates from the allowlisted
            # module.
            return

        raise PluginVerificationError(
            f"Plugin '{metadata.name}' is already registered and cannot be replaced."
        )

    REGISTRY[metadata.name] = (metadata, plugin)


def dispatch(name: str, payload: dict) -> dict:
    """Dispatch a payload to a registered plugin."""

    entry = REGISTRY.get(name)
    if not entry:
        raise KeyError(f"Plugin '{name}' not found")
    _meta, plugin = entry
    return plugin.run(payload)


def _select_entry_points(group: str) -> Sequence[EntryPoint]:
    """Return the entry points registered for ``group`` in a stable sequence."""

    eps = entry_points()
    if hasattr(eps, "select"):
        return tuple(eps.select(group=group))

    # Compatibility shim for older Python versions where ``select`` is absent.
    selected: Iterable[EntryPoint]
    if isinstance(eps, dict):  # type: ignore[unreachable]
        selected = eps.get(group, [])
    else:
        selected = [ep for ep in eps if ep.group == group]
    return tuple(selected)


def _allowlisted_modules() -> dict[str, str]:
    """Map fully qualified module names to allowlist keys."""

    mapping: dict[str, str] = {}
    package_prefix = f"{__name__}."
    for module_key, spec in ALLOWED_PLUGINS.items():
        candidate = spec.module
        if candidate.startswith(package_prefix):
            full_name = candidate
        else:
            full_name = f"{package_prefix}{candidate}"
        mapping[full_name] = module_key
        mapping[candidate] = module_key
        mapping[module_key] = module_key
    return mapping


def _load_entry_point(ep: EntryPoint, module_key: str) -> None:
    """Load and register the plugin exposed by ``ep`` after verification."""

    spec = ALLOWED_PLUGINS[module_key]
    load_plugin_module(module_key)

    factory = ep.load()
    if not callable(factory):
        raise PluginVerificationError(
            f"Entry point '{ep.name}' for module '{ep.module}' is not callable."
        )

    plugin_bundle = factory()
    if not isinstance(plugin_bundle, tuple) or len(plugin_bundle) != 2:
        raise PluginVerificationError(
            f"Entry point '{ep.name}' must return a (plugin, metadata) tuple."
        )

    plugin, metadata = plugin_bundle
    if not isinstance(metadata, PluginMetadata):
        raise PluginVerificationError(
            f"Entry point '{ep.name}' returned invalid metadata object {type(metadata)!r}."
        )
    expected_name = spec.marker or metadata.name
    if metadata.name != expected_name:
        raise PluginVerificationError(
            "Entry point '%s' returned metadata for unexpected plugin '%s'"
            % (ep.name, metadata.name),
        )

    register(plugin, metadata)


def discover(group: str = "cognitive_core.plugins") -> None:
    """Discover and load allowlisted plugins defined via entry points."""

    selected = _select_entry_points(group)
    if not selected:
        return

    allowlisted = _allowlisted_modules()
    for ep in selected:
        module_key = allowlisted.get(ep.module)
        if module_key is None:
            raise PluginVerificationError(
                f"Entry point '{ep.name}' references unallowlisted module '{ep.module}'."
            )
        _load_entry_point(ep, module_key)
