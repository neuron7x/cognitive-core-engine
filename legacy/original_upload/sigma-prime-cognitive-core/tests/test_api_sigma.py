from fastapi.testclient import TestClient

from api.app import app

client = TestClient(app)


def test_healthz():
    r = client.get("/v1/healthz")
    assert r.status_code == 200
    assert r.json().get("ok") is True


def test_sigma_happy_path():
    body = {
        "phi": 0.5,
        "psi": 0.8,
        "epsilon": 0.3,
        "tau": 0.7,
        "eta": 0.2,
        "alpha": 0.3,
        "recurrence": 0.4,
    }
    r = client.post("/v1/sigma", json=body)
    assert r.status_code == 200
    data = r.json()
    assert "sigma" in data and data["sigma"] >= 0


def test_sigma_validation_error():
    body = {"phi": -1, "psi": 0, "epsilon": 0, "tau": 0, "eta": 0, "alpha": 0, "recurrence": 0}
    r = client.post("/v1/sigma", json=body)
    assert r.status_code == 422  # Pydantic validation before handler
