from fastapi.testclient import TestClient

from cognitive_core import config
from cognitive_core.api.main import app

API_KEY = "test-key"

client = TestClient(app)


def _authorized_get(path: str):
    config.settings.api_key = API_KEY
    return client.get(path, headers={"X-API-Key": API_KEY})


def test_root_endpoint():
    r = _authorized_get("/")
    assert r.status_code == 200
    assert "name" in r.json()


def test_health_endpoint():
    r = _authorized_get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_security_headers_present():
    r = _authorized_get("/")
    assert (
        r.headers["Strict-Transport-Security"]
        == "max-age=63072000; includeSubDomains; preload"
    )
    assert r.headers["X-Frame-Options"] == "DENY"
    assert r.headers["X-Content-Type-Options"] == "nosniff"
