import importlib
import pytest

pytest.importorskip("fastapi")
pytest.importorskip("pydantic_settings")

from cognitive_core.api import auth
from cognitive_core import config


@pytest.mark.integration
def test_health_without_api_key_unset(api_client, monkeypatch):
    monkeypatch.delenv("COG_API_KEY", raising=False)
    importlib.reload(config)
    importlib.reload(auth)

    response = api_client.get("/api/health")
    assert response.status_code == 200


@pytest.mark.integration
def test_health_with_empty_api_key(api_client, monkeypatch):
    monkeypatch.setenv("COG_API_KEY", "")
    importlib.reload(config)
    importlib.reload(auth)

    response = api_client.get("/api/health")
    assert response.status_code == 403
