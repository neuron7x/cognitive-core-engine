import pytest

from cognitive_core.api import auth
from cognitive_core.config import Settings


@pytest.mark.integration
def test_health_without_api_key_header(api_client, monkeypatch):
    monkeypatch.delenv("COG_API_KEY", raising=False)
    monkeypatch.setattr(auth, "settings", Settings())
    response = api_client.get("/api/health")
    assert response.status_code == 200
