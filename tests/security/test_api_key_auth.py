import importlib

import pytest
from fastapi.testclient import TestClient


def _build_client():
    import cognitive_core.api.main as main
    importlib.reload(main)
    return TestClient(main.app)


def _reset(monkeypatch, api_key=None, api_keys=None):
    for key in ("COG_API_KEY", "COG_API_KEYS"):
        monkeypatch.delenv(key, raising=False)
    if api_key is not None:
        monkeypatch.setenv("COG_API_KEY", api_key)
    if api_keys is not None:
        monkeypatch.setenv("COG_API_KEYS", api_keys)
    import cognitive_core.config as config
    importlib.reload(config)
    import cognitive_core.api.auth as auth
    importlib.reload(auth)
    return _build_client()


def test_valid_key_allows(monkeypatch):
    client = _reset(monkeypatch, api_key="secret")
    r = client.get("/api/health", headers={"X-API-Key": "secret"})
    assert r.status_code == 200


def test_invalid_key_denied(monkeypatch):
    client = _reset(monkeypatch, api_key="secret")
    r = client.get("/api/health", headers={"X-API-Key": "wrong"})
    assert r.status_code == 403


def test_no_key_unrestricted(monkeypatch):
    client = _reset(monkeypatch)
    r = client.get("/api/health")
    assert r.status_code == 200


def test_empty_key_blocks(monkeypatch):
    client = _reset(monkeypatch, api_key="")
    r = client.get("/api/health")
    assert r.status_code == 403


def test_multiple_keys(monkeypatch):
    client = _reset(monkeypatch, api_keys="k1,k2")
    assert client.get("/api/health", headers={"X-API-Key": "k2"}).status_code == 200
    assert client.get("/api/health", headers={"X-API-Key": "bad"}).status_code == 403


from hypothesis import given, strategies as st


@given(st.text().filter(lambda s: s not in {"good", ""}))
def test_random_invalid_keys(monkeypatch, key):
    client = _reset(monkeypatch, api_key="good")
    r = client.get("/api/health", headers={"X-API-Key": key})
    assert r.status_code == 403
