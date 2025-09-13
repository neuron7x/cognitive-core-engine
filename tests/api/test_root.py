from fastapi.testclient import TestClient

from cognitive_core.api.main import app

client = TestClient(app)


def test_root_endpoint():
    r = client.get("/")
    assert r.status_code == 200
    assert "name" in r.json()


def test_health_endpoint():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
