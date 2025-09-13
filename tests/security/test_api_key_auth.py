import pytest
from unittest.mock import Mock

from cognitive_core.api import auth
from cognitive_core.config import Settings


@pytest.mark.integration
def test_api_key_enforced(api_client, monkeypatch):
    monkeypatch.setenv("COG_API_KEYS", "secret")
    monkeypatch.setattr(auth, "settings", Settings())
    mock_counter = Mock()
    monkeypatch.setattr(auth, "API_KEY_FAILURES", mock_counter)

    r = api_client.get("/api/health")
    assert r.status_code == 403
    mock_counter.inc.assert_called_once()

    r2 = api_client.get("/api/health", headers={"X-API-Key": "secret"})
    assert r2.status_code == 200
    assert mock_counter.inc.call_count == 1


@pytest.mark.integration
def test_empty_api_key_requires_header(api_client, monkeypatch):
    monkeypatch.setenv("COG_API_KEYS", "")
    monkeypatch.setattr(auth, "settings", Settings())

    r = api_client.get("/api/health")
    assert r.status_code == 403

    r2 = api_client.get("/api/health", headers={"X-API-Key": ""})
    assert r2.status_code == 200
