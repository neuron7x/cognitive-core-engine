import os

from fastapi.testclient import TestClient

from cognitive_core import config
from cognitive_core.api import auth
from cognitive_core.api.main import app

os.environ.setdefault("COG_API_KEY", "e2e-secret")
API_KEY = os.environ["COG_API_KEY"]
config.settings = config.Settings(api_key=API_KEY)
auth.settings = config.settings

client = TestClient(app)


def _headers() -> dict[str, str]:
    config.settings = config.Settings(api_key=API_KEY)
    auth.settings = config.settings
    return {"X-API-Key": API_KEY}


def test_health():
    r = client.get("/api/health", headers=_headers())
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_dot_endpoint():
    r = client.post(
        "/api/dot",
        json={"a": [1, 2], "b": [3, 4]},
        headers=_headers(),
    )
    assert r.status_code == 200 and r.json()["result"] == 11.0
