import pytest

from cognitive_core import config
from cognitive_core.api import auth


@pytest.mark.integration
def test_api_key_enforced(api_client, monkeypatch):
    monkeypatch.setenv("COG_API_KEY", "secret")
    monkeypatch.setattr(config, "settings", config.Settings())
    monkeypatch.setattr(auth, "settings", config.settings)

    r = api_client.get("/api/health")
    assert r.status_code == 403

    r2 = api_client.get("/api/health", headers={"X-API-Key": "secret"})
    assert r2.status_code == 200
