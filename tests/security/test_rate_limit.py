import importlib

import pytest
from fastapi.testclient import TestClient

from cognitive_core.api import rate_limit
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
    monkeypatch.setenv("COG_RATE_LIMIT_RPS", "0")
    monkeypatch.setenv("COG_RATE_LIMIT_BURST", "2")
    importlib.reload(config)
    importlib.reload(rate_limit)
    monkeypatch.setattr(rate_limit, "RedisBucketLimiter", DummyLimiter)
    importlib.reload(main)
    client = TestClient(main.app)
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/health").status_code == 429
