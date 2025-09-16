import importlib

import pytest
from fastapi.testclient import TestClient

from cognitive_core import config
from cognitive_core.api import auth, main, rate_limit


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
