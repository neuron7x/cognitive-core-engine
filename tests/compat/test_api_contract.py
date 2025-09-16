import os

from fastapi.testclient import TestClient

os.environ.setdefault("COG_API_KEY", "contract-secret")

from cognitive_core import config
from cognitive_core.api import auth
from cognitive_core.api.main import app

API_KEY = os.environ["COG_API_KEY"]
config.settings = config.Settings(api_key=API_KEY)
auth.settings = config.settings

client = TestClient(app)
API_HEADERS = {"X-API-Key": API_KEY}


def _ensure_api_key() -> None:
    config.settings = config.Settings(api_key=API_KEY)
    auth.settings = config.settings


def test_contract_health_shape():
    _ensure_api_key()
    r = client.get("/api/health", headers=API_HEADERS)
    assert r.status_code == 200
    j = r.json()
    assert set(j.keys()) == {"status"} and j["status"] == "ok"


def test_contract_dot_shape():
    _ensure_api_key()
    r = client.post(
        "/api/dot",
        json={"a": [1, 2, 3], "b": [4, 5, 6]},
        headers=API_HEADERS,
    )
    assert r.status_code == 200
    j = r.json()
    assert "result" in j and isinstance(j["result"], (int, float))


def test_contract_solve2x2_shape():
    _ensure_api_key()
    r = client.post(
        "/api/solve2x2",
        json={"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6},
        headers=API_HEADERS,
    )
    assert r.status_code == 200
    j = r.json()
    assert "x" in j and "y" in j
