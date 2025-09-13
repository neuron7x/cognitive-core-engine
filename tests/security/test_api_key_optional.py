import pytest

from cognitive_core.api import auth


@pytest.mark.integration
def test_health_without_api_key(api_client, monkeypatch):
    monkeypatch.setattr(auth.settings, "api_key", None)
    response = api_client.get("/api/health")
    assert response.status_code == 200
