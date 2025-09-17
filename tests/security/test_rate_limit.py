import importlib

import pytest
from fastapi.testclient import TestClient

from cognitive_core.api import auth, rate_limit
from cognitive_core.api import main
from cognitive_core import config


class DummyLimiter:
    def __init__(self, *args, **kwargs):
        self.capacity = kwargs.get("capacity", 1)
        self.tokens: dict[str, float] = {}

    def allow(self, token: str, needed: float = 1.0) -> bool:  # pragma: no cover - simple
        remaining = self.tokens.get(token, float(self.capacity))
        if remaining >= needed:
            self.tokens[token] = remaining - needed
            return True
        return False


@pytest.mark.integration
def test_rate_limit_blocks_after_burst(monkeypatch):
    monkeypatch.setenv("COG_API_KEY", "rate-limit-key")
    monkeypatch.setenv("COG_RATE_LIMIT_RPS", "0")
    monkeypatch.setenv("COG_RATE_LIMIT_BURST", "2")
    importlib.reload(config)
    monkeypatch.setattr(
        config,
        "settings",
        config.Settings(api_key="rate-limit-key", rate_limit_rps=0.0, rate_limit_burst=2),
    )
    monkeypatch.setattr(auth, "settings", config.settings)
    importlib.reload(rate_limit)
    monkeypatch.setattr(rate_limit, "RedisBucketLimiter", DummyLimiter)
    importlib.reload(main)
    client = TestClient(main.app)
    headers = {"X-API-Key": "rate-limit-key"}
    assert client.get("/api/health", headers=headers).status_code == 200
    assert client.get("/api/health", headers=headers).status_code == 200
    assert client.get("/api/health", headers=headers).status_code == 429


@pytest.mark.integration
def test_rate_limit_shared_ip_budget_blocks_rotating_keys(monkeypatch):
    monkeypatch.setenv("COG_API_KEY", "key-1,key-2,key-3")
    monkeypatch.setenv("COG_RATE_LIMIT_RPS", "0")
    monkeypatch.setenv("COG_RATE_LIMIT_BURST", "2")

    importlib.reload(config)
    monkeypatch.setattr(
        config,
        "settings",
        config.Settings(
            api_key="key-1,key-2,key-3",
            rate_limit_rps=0.0,
            rate_limit_burst=2,
        ),
    )
    monkeypatch.setattr(auth, "settings", config.settings)
    importlib.reload(rate_limit)
    monkeypatch.setattr(rate_limit, "RedisBucketLimiter", DummyLimiter)
    importlib.reload(main)

    client = TestClient(main.app)

    assert client.get("/api/health", headers={"X-API-Key": "key-1"}).status_code == 200
    assert client.get("/api/health", headers={"X-API-Key": "key-2"}).status_code == 200
    assert client.get("/api/health", headers={"X-API-Key": "key-3"}).status_code == 429


def test_in_memory_limiter_prunes_expired_tokens(monkeypatch):
    current_time = 0.0
    monkeypatch.setattr(rate_limit.time, "time", lambda: current_time)

    limiter = rate_limit.InMemoryBucketLimiter(capacity=3, refill_per_sec=1.0)

    tokens = [f"token-{idx}" for idx in range(5)]
    for token in tokens:
        assert limiter.allow(token)

    assert len(limiter._state) == len(tokens)

    current_time += 10.0
    limiter.allow("prune-only", needed=0)

    assert limiter._state == {}
    assert not limiter._expirations
