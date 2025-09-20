"""Checks for deployment unit file hygiene."""
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SERVICE_PATH = PROJECT_ROOT / "deployment" / "cognitive_core.service"


def test_service_loads_external_environment_file() -> None:
    contents = SERVICE_PATH.read_text(encoding="utf-8")
    assert "EnvironmentFile=" in contents, "Service should load secrets from an external environment file."


def test_service_does_not_embed_placeholder_secrets() -> None:
    contents = SERVICE_PATH.read_text(encoding="utf-8")
    forbidden_tokens = {"changeme", "COG_API_KEY="}
    for token in forbidden_tokens:
        assert token not in contents, f"Service file should not include placeholder secret '{token}'."
