from __future__ import annotations

import hashlib
import importlib
from dataclasses import dataclass
from pathlib import Path


PLUGIN_MARKER = "__plugin__"
_PLUGIN_MARKER_BYTES = PLUGIN_MARKER.encode("utf-8")


@dataclass(frozen=True)
class PluginSpec:
    """Specification describing an allowed plugin module."""

    module: str
    sha256: str
    marker: str | None = None


class PluginVerificationError(RuntimeError):
    """Raised when a plugin fails integrity or authenticity checks."""


# The allowlist maps module dotted-paths relative to this package to a
# :class:`PluginSpec`. The SHA-256 hash guards the module contents against
# tampering.
ALLOWED_PLUGINS: dict[str, PluginSpec] = {
    "example.math_plugin": PluginSpec(
        module="example.math_plugin",
        sha256="2ead25265c1b1e12488b6350293b00d33c896ead30df01f7b9bf66707c90ec63",
        marker="math.dot",
    )
}


def load_plugins() -> None:
    """Scan the plugins package and import allowed modules only.

    Importing modules causes them to register themselves with the plugin
    registry via the ``register`` function. Only modules present in
    :data:`ALLOWED_PLUGINS` with matching hashes and plugin markers are loaded.
    """

    base_dir = Path(__file__).resolve().parent
    package = __name__.rsplit(".", 1)[0]

    for path in base_dir.rglob("*.py"):
        if path.name in {"__init__.py", "plugin_loader.py"}:
            continue

        rel_parts = path.relative_to(base_dir).with_suffix("").parts
        module_key = ".".join(rel_parts)
        contents = path.read_bytes()
        has_marker = _PLUGIN_MARKER_BYTES in contents

        spec = ALLOWED_PLUGINS.get(module_key)
        if not spec:
            continue
        if not has_marker:
            raise PluginVerificationError(
                f"Allowlisted plugin '{module_key}' is missing the '{PLUGIN_MARKER}' marker."
            )

        digest = hashlib.sha256(contents).hexdigest()
        if digest != spec.sha256:
            raise PluginVerificationError(
                "Plugin hash mismatch for '%s': expected %s but got %s"
                % (module_key, spec.sha256, digest)
            )

        module_name = ".".join((package, *rel_parts))
        module = importlib.import_module(module_name)

        if not hasattr(module, PLUGIN_MARKER):
            raise PluginVerificationError(
                f"Plugin '{module_key}' is missing the required '{PLUGIN_MARKER}' marker."
            )

        marker_value = getattr(module, PLUGIN_MARKER)
        if spec.marker is not None and marker_value != spec.marker:
            raise PluginVerificationError(
                "Plugin marker mismatch for '%s': expected %s but got %s"
                % (module_key, spec.marker, marker_value)
            )
