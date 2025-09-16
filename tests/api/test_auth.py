import asyncio
import importlib
import os

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from cognitive_core.api import auth
from cognitive_core.api.main import app
from cognitive_core import config


client = TestClient(app)


def _reload():
    """Reload config and auth after environment changes."""
    importlib.reload(config)
    importlib.reload(auth)
    configured = os.getenv("COG_API_KEY")
    if configured is None:
        configured = ""

    config.settings.api_key = configured
    auth.settings.api_key = configured


def test_server_error_when_api_key_missing(monkeypatch):
    monkeypatch.delenv("COG_API_KEY", raising=False)
    _reload()
    r = client.get("/api/health")
    assert r.status_code == 500


def test_server_error_when_api_key_empty(monkeypatch):
    monkeypatch.setenv("COG_API_KEY", "")
    _reload()
    r = client.get("/api/health")
    assert r.status_code == 500


def test_allows_valid_api_key(monkeypatch):
    monkeypatch.setenv("COG_API_KEY", "secret")
    _reload()
    r = client.get("/api/health", headers={"X-API-Key": "secret"})
    assert r.status_code == 200


def test_rejects_invalid_api_key(monkeypatch):
    monkeypatch.setenv("COG_API_KEY", "secret")
    _reload()
    r = client.get("/api/health", headers={"X-API-Key": "bad"})
    assert r.status_code == 403


def test_verify_api_key_rejects_spoofed_value(monkeypatch):
    monkeypatch.setenv("COG_API_KEY", "secret")
    _reload()
    with pytest.raises(HTTPException) as exc:
        asyncio.run(auth.verify_api_key("spoofed"))

    assert exc.value.status_code == 403


def test_verify_api_key_rejects_missing_value(monkeypatch):
    """Simulate tampering by stripping the API key header entirely."""

    monkeypatch.setenv("COG_API_KEY", "secret")
    _reload()

    with pytest.raises(HTTPException) as exc:
        asyncio.run(auth.verify_api_key(None))

    assert exc.value.status_code == 403
