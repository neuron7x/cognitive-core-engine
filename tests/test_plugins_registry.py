from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

from cognitive_core.plugins import REGISTRY, dispatch
from cognitive_core.plugins.plugin_loader import (
    ALLOWED_PLUGINS,
    PluginSpec,
    PluginVerificationError,
    load_plugins,
)


PLUGINS_DIR = Path(__file__).resolve().parents[1] / "src" / "cognitive_core" / "plugins"
PLUGIN_FILE = PLUGINS_DIR / "example" / "math_plugin.py"


def _reset_plugin_modules() -> None:
    for name in list(sys.modules):
        if name == "cognitive_core.plugins.example" or name.startswith(
            "cognitive_core.plugins.example."
        ):
            sys.modules.pop(name)


@pytest.fixture(autouse=True)
def reset_plugin_environment():
    """Ensure plugin registry and modules are reset for each test."""

    REGISTRY.clear()
    _reset_plugin_modules()
    yield
    REGISTRY.clear()
    _reset_plugin_modules()


def test_math_plugin_registration_and_execution():
    load_plugins()

    assert "math.dot" in REGISTRY
    meta, _ = REGISTRY["math.dot"]
    assert meta.version == "1.0.0"
    result = dispatch("math.dot", {"a": [1, 2], "b": [3, 4]})
    assert result["result"] == 11


def test_load_plugins_skips_unapproved_modules():
    rogue_path = PLUGINS_DIR / "example" / "rogue_plugin.py"
    rogue_path.write_text(
        "__plugin__ = 'rogue.module'\nraise RuntimeError('rogue plugin imported')\n"
    )

    try:
        load_plugins()
        assert "math.dot" in REGISTRY
        assert "cognitive_core.plugins.example.rogue_plugin" not in sys.modules
        assert all(entry[0].name != "rogue.module" for entry in REGISTRY.values())
    finally:
        rogue_path.unlink(missing_ok=True)


def test_load_plugins_detects_hash_mismatch(monkeypatch):
    spec = ALLOWED_PLUGINS["example.math_plugin"]
    tampered_spec = PluginSpec(module=spec.module, sha256="0" * 64, marker=spec.marker)
    monkeypatch.setitem(ALLOWED_PLUGINS, "example.math_plugin", tampered_spec)

    with pytest.raises(PluginVerificationError):
        load_plugins()


def test_load_plugins_detects_missing_marker(monkeypatch):
    spec = ALLOWED_PLUGINS["example.math_plugin"]
    original_source = PLUGIN_FILE.read_text()
    marker_line = "__plugin__ = \"math.dot\"\n\n"
    if marker_line not in original_source:
        pytest.fail("Expected plugin marker declaration to be present")
    modified_source = original_source.replace(marker_line, "")
    PLUGIN_FILE.write_text(modified_source)

    new_hash = hashlib.sha256(modified_source.encode("utf-8")).hexdigest()
    monkeypatch.setitem(
        ALLOWED_PLUGINS,
        "example.math_plugin",
        PluginSpec(module=spec.module, sha256=new_hash, marker=spec.marker),
    )

    try:
        with pytest.raises(PluginVerificationError):
            load_plugins()
    finally:
        PLUGIN_FILE.write_text(original_source)
