import importlib

from fastapi.testclient import TestClient

from cognitive_core.api.main import app
from cognitive_core.api import auth
from cognitive_core import config


client = TestClient(app)


def _reload():
    """Reload config and auth after environment changes."""
    importlib.reload(config)
    importlib.reload(auth)


def test_no_auth_when_api_key_none(monkeypatch):
    monkeypatch.delenv("COG_API_KEY", raising=False)
    _reload()
    r = client.get("/api/health")
    assert r.status_code == 200


def test_requires_auth_when_api_key_empty(monkeypatch):
    monkeypatch.setenv("COG_API_KEY", "")
    _reload()
    r = client.get("/api/health")
    assert r.status_code == 403
    r = client.get("/api/health", headers={"X-API-Key": ""})
    assert r.status_code == 200


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
