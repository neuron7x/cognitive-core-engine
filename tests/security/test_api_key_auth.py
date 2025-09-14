import importlib

import pytest
from hypothesis import assume, given, strategies as st

from cognitive_core import config
from cognitive_core.api import auth


@pytest.mark.integration
def test_api_key_enforced(api_client, monkeypatch):
    monkeypatch.setenv("COG_API_KEY", "secret")
    importlib.reload(config)
    importlib.reload(auth)

    r = api_client.get("/api/health")
    assert r.status_code == 403

    r2 = api_client.get("/api/health", headers={"X-API-Key": "secret"})
    assert r2.status_code == 200


@pytest.mark.integration
def test_no_api_key_configured(api_client, monkeypatch):
    monkeypatch.delenv("COG_API_KEY", raising=False)
    importlib.reload(config)
    importlib.reload(auth)

    r = api_client.get("/api/health")
    assert r.status_code == 200


@pytest.mark.integration
def test_empty_api_key_requires_header(api_client, monkeypatch):
    monkeypatch.setenv("COG_API_KEY", "")
    importlib.reload(config)
    importlib.reload(auth)

    r = api_client.get("/api/health")
    assert r.status_code == 403

    r2 = api_client.get("/api/health", headers={"X-API-Key": ""})
    assert r2.status_code == 200


@pytest.mark.integration
def test_multiple_api_keys(api_client, monkeypatch):
    monkeypatch.setenv("COG_API_KEY", "secret,altsecret")
    importlib.reload(config)
    importlib.reload(auth)

    r_missing = api_client.get("/api/health")
    assert r_missing.status_code == 403

    r_valid = api_client.get("/api/health", headers={"X-API-Key": "secret"})
    assert r_valid.status_code == 200

    r_alt_valid = api_client.get("/api/health", headers={"X-API-Key": "altsecret"})
    assert r_alt_valid.status_code == 200

    r_invalid = api_client.get("/api/health", headers={"X-API-Key": "bad"})
    assert r_invalid.status_code == 403


@given(st.text())
@pytest.mark.integration
def test_random_invalid_keys_rejected(random_key, api_client, monkeypatch):
    monkeypatch.setenv("COG_API_KEY", "secret")
    importlib.reload(config)
    importlib.reload(auth)

    assume(random_key != "secret")
    r = api_client.get("/api/health", headers={"X-API-Key": random_key})
    assert r.status_code == 403


@pytest.mark.integration
def test_health_allows_access_when_key_unset(api_client, monkeypatch):
    monkeypatch.delenv("COG_API_KEY", raising=False)
    importlib.reload(config)
    importlib.reload(auth)

    response = api_client.get("/api/health")
    assert response.status_code == 200


@pytest.mark.integration
def test_health_rejects_without_key_when_env_empty(api_client, monkeypatch):
    monkeypatch.setenv("COG_API_KEY", "")
    importlib.reload(config)
    importlib.reload(auth)

    response = api_client.get("/api/health")
    assert response.status_code == 403
