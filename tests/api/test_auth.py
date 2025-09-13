from fastapi.testclient import TestClient

from cognitive_core.api.main import app
from cognitive_core.api import auth
from cognitive_core.config import Settings


client = TestClient(app)


def test_no_auth_when_api_keys_none(monkeypatch):
    monkeypatch.delenv("COG_API_KEYS", raising=False)
    monkeypatch.setattr(auth, "settings", Settings())
    r = client.get("/api/health")
    assert r.status_code == 200


def test_requires_auth_when_api_keys_empty(monkeypatch):
    monkeypatch.setenv("COG_API_KEYS", "")
    monkeypatch.setattr(auth, "settings", Settings())
    r = client.get("/api/health")
    assert r.status_code == 403
    r = client.get("/api/health", headers={"X-API-Key": ""})
    assert r.status_code == 200
