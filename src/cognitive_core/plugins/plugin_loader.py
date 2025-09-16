from __future__ import annotations

import hashlib
import importlib
from dataclasses import dataclass
from pathlib import Path

PLUGIN_MARKER = "__plugin__"
_PLUGIN_MARKER_BYTES = PLUGIN_MARKER.encode("utf-8")
_PLUGINS_ROOT = Path(__file__).resolve().parent
_PLUGINS_PACKAGE = __name__.rsplit(".", 1)[0]


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
        sha256="a2f3131159f6bd0175c2af9a9e01901540d52c344b6ebaf1d9c60c1cb38367f5",
        marker="math.dot",
    )
}


def _normalise_spec_module(module: str, spec: PluginSpec) -> tuple[str, str]:
    """Return the relative and fully qualified module names for ``spec``."""

    relative = spec.module
    if relative.startswith(f"{_PLUGINS_PACKAGE}."):
        relative = relative[len(_PLUGINS_PACKAGE) + 1 :]

    if relative != module:
        raise PluginVerificationError(
            f"Allowlist entry for '{module}' references mismatched module '{spec.module}'."
        )

    full = f"{_PLUGINS_PACKAGE}.{relative}"
    return relative, full


def _resolve_plugin_path(module: str) -> Path:
    """Return the absolute path to a plugin module inside the plugins package."""

    parts = module.split(".")
    if any(part in {"", ".", ".."} or not part.isidentifier() for part in parts):
        raise PluginVerificationError(f"Invalid module path '{module}' in plugin allowlist.")

    candidate = _PLUGINS_ROOT.joinpath(*parts)
    if candidate.is_dir():
        module_path = candidate / "__init__.py"
    else:
        module_path = candidate.with_suffix(".py")

    if not module_path.exists():
        raise ModuleNotFoundError(f"Plugin module '{module}' not found at {module_path}.")

    resolved = module_path.resolve(strict=True)
    try:
        resolved.relative_to(_PLUGINS_ROOT)
    except ValueError as exc:
        raise PluginVerificationError(
            f"Resolved path for plugin '{module}' escapes the plugins directory."
        ) from exc

    if not resolved.is_file():
        raise PluginVerificationError(f"Plugin '{module}' resolved path {resolved} is not a file.")

    return resolved


def _load_plugin_from_spec(module: str, spec: PluginSpec) -> None:
    """Load a single plugin described by ``spec``."""

    relative, full = _normalise_spec_module(module, spec)
    module_path = _resolve_plugin_path(relative)

    contents = module_path.read_bytes()
    if _PLUGIN_MARKER_BYTES not in contents:
        raise PluginVerificationError(
            f"Allowlisted plugin '{module}' is missing the '{PLUGIN_MARKER}' marker."
        )

    digest = hashlib.sha256(contents).hexdigest()
    if digest != spec.sha256:
        raise PluginVerificationError(
            "Plugin hash mismatch for '%s': expected %s but got %s" % (module, spec.sha256, digest)
        )

    importlib.invalidate_caches()
    module_obj = importlib.import_module(full)

    if not hasattr(module_obj, PLUGIN_MARKER):
        raise PluginVerificationError(
            f"Plugin '{module}' is missing the required '{PLUGIN_MARKER}' marker."
        )

    marker_value = getattr(module_obj, PLUGIN_MARKER)
    if spec.marker is not None and marker_value != spec.marker:
        raise PluginVerificationError(
            "Plugin marker mismatch for '%s': expected %s but got %s"
            % (module, spec.marker, marker_value)
        )


def load_plugin_module(module: str) -> PluginSpec:
    """Load a single allowlisted plugin module after integrity checks."""

    spec = ALLOWED_PLUGINS.get(module)
    if spec is None:
        raise PluginVerificationError(
            f"Plugin module '{module}' is not in the allowlist and cannot be installed."
        )

    _load_plugin_from_spec(module, spec)
    return spec


def load_plugins() -> None:
    """Import all allowlisted plugins after verifying their integrity."""

    for module, spec in ALLOWED_PLUGINS.items():
        _load_plugin_from_spec(module, spec)
