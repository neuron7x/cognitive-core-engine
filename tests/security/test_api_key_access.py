import pytest

pytest.importorskip("fastapi")
pytest.importorskip("pydantic_settings")

from cognitive_core.api import auth
from cognitive_core.config import Settings


@pytest.mark.integration
def test_health_without_api_key_unset(api_client, monkeypatch):
    monkeypatch.delenv("COG_API_KEY", raising=False)
    monkeypatch.setattr(auth, "settings", Settings())

    response = api_client.get("/api/health")
    assert response.status_code == 200


@pytest.mark.integration
def test_health_with_empty_api_key(api_client, monkeypatch):
    monkeypatch.setenv("COG_API_KEY", "")
    monkeypatch.setattr(auth, "settings", Settings())

    response = api_client.get("/api/health")
    assert response.status_code == 403
