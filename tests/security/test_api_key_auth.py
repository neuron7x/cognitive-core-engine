import pytest

from cognitive_core.api import auth


@pytest.mark.integration
def test_api_key_enforced(api_client):
    original = auth.settings.api_key
    auth.settings.api_key = "secret"
    try:
        r = api_client.get("/api/health")
        assert r.status_code == 403
        r2 = api_client.get("/api/health", headers={"X-API-Key": "secret"})
        assert r2.status_code == 200
    finally:
        auth.settings.api_key = original
