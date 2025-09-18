from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path


def _load_module(module_name: str, file_path: Path, monkeypatch):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise RuntimeError(f"Unable to load module {module_name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, module_name, module)
    spec.loader.exec_module(module)
    return module


def test_settings_reads_environment_when_third_party_missing(monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    stub_path = repo_root / "src" / "pydantic_settings" / "__init__.py"
    settings_path = repo_root / "src" / "cognitive_core" / "config" / "settings.py"

    stub_module = _load_module("pydantic_settings", stub_path, monkeypatch)

    monkeypatch.setenv("COG_API_KEY", "env-secret")

    settings_module = _load_module("tests.config._stubbed_settings", settings_path, monkeypatch)

    settings = settings_module.Settings()

    assert settings_module.BaseSettings is stub_module.BaseSettings
    assert settings.api_key == "env-secret"

    # Ensure the stub leaves unrelated environment variables untouched.
    assert os.environ["COG_API_KEY"] == "env-secret"
