import importlib

import pytest
from fastapi.testclient import TestClient

from cognitive_core.api import auth, rate_limit
from cognitive_core.api import main
from cognitive_core import config


class DummyLimiter:
    def __init__(self, *args, **kwargs):
        self.capacity = kwargs.get("capacity", 1)
        self.tokens = self.capacity

    def allow(self, token: str, needed: float = 1.0) -> bool:  # pragma: no cover - simple
        if self.tokens >= needed:
            self.tokens -= needed
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


def test_in_memory_limiter_prunes_tokens_when_no_refill(monkeypatch):
    current_time = 0.0
    monkeypatch.setattr(rate_limit.time, "time", lambda: current_time)

    limiter = rate_limit.InMemoryBucketLimiter(capacity=2, refill_per_sec=0.0)

    tokens = [f"no-refill-{idx}" for idx in range(4)]
    for token in tokens:
        assert limiter.allow(token)

    assert len(limiter._state) == len(tokens)

    current_time += rate_limit.InMemoryBucketLimiter.NO_REFILL_TTL + 1.0
    limiter.allow("prune-trigger", needed=0)

    assert limiter._state == {}
    assert not limiter._expirations
