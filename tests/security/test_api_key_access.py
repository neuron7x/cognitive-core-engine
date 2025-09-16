import importlib

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("pydantic_settings")

auth = importlib.import_module("cognitive_core.api.auth")
config = importlib.import_module("cognitive_core.config")


@pytest.mark.integration
def test_health_without_api_key_unset(api_client, monkeypatch):
    monkeypatch.delenv("COG_API_KEY", raising=False)
    importlib.reload(config)
    importlib.reload(auth)

    response = api_client.get("/api/health")
    assert response.status_code == 500


@pytest.mark.integration
def test_health_with_empty_api_key(api_client, monkeypatch):
    monkeypatch.setenv("COG_API_KEY", "")
    importlib.reload(config)
    importlib.reload(auth)

    response = api_client.get("/api/health")
    assert response.status_code == 500
