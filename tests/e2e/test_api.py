import os

import pytest
from fastapi.testclient import TestClient

from cognitive_core import config
from cognitive_core.api import auth, rate_limit
from cognitive_core.api.main import app


@pytest.fixture
def api_key(monkeypatch: pytest.MonkeyPatch) -> str:
    original_config_settings = config.settings
    original_auth_settings = auth.settings

    monkeypatch.setenv("COG_API_KEY", "e2e-secret")
    monkeypatch.setattr(rate_limit, "RedisBucketLimiter", None, raising=False)
    api_key = os.environ["COG_API_KEY"]
    config.settings = config.Settings(api_key=api_key)
    auth.settings = config.settings

    yield api_key

    config.settings = original_config_settings
    auth.settings = original_auth_settings


@pytest.fixture
def client(api_key: str):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(api_key: str) -> dict[str, str]:
    return {"X-API-Key": api_key}


def test_health(client: TestClient, auth_headers: dict[str, str]):
    response = client.get("/api/health", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_dot_endpoint(client: TestClient, auth_headers: dict[str, str]):
    response = client.post(
        "/api/dot",
        json={"a": [1, 2], "b": [3, 4]},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["result"] == 11.0
