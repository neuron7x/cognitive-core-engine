from fastapi.testclient import TestClient

from cognitive_core.api import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_dot_endpoint():
    r = client.post("/api/dot", json={"a": [1, 2], "b": [3, 4]})
    assert r.status_code == 200 and r.json()["result"] == 11.0
