import hashlib
import importlib
import logging
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from cognitive_core.api import auth, rate_limit
from cognitive_core.api import main
from cognitive_core import config
import cognitive_core.rate_limiter as core_rate_limiter
from cognitive_core.rate_limiter import RateLimiterUnavailableError


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


@pytest.mark.integration
def test_rate_limit_ignores_untrusted_forwarded_header(monkeypatch):
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
            trust_proxy_headers=False,
        ),
    )
    monkeypatch.setattr(auth, "settings", config.settings)
    importlib.reload(rate_limit)
    monkeypatch.setattr(rate_limit, "RedisBucketLimiter", DummyLimiter)
    importlib.reload(main)

    client = TestClient(main.app)

    forwarded_ips = ["8.8.8.8", "1.1.1.1", "9.9.9.9"]
    for idx, ip in enumerate(forwarded_ips, start=1):
        headers = {"X-API-Key": f"key-{idx}", "X-Forwarded-For": ip}
        response = client.get("/api/health", headers=headers)
        if idx < 3:
            assert response.status_code == 200
        else:
            assert response.status_code == 429


@pytest.mark.integration
def test_rate_limit_trusts_forwarded_header_for_distinct_clients(monkeypatch):
    monkeypatch.setenv("COG_API_KEY", "key-1,key-2,key-3")
    monkeypatch.setenv("COG_RATE_LIMIT_RPS", "0")
    monkeypatch.setenv("COG_RATE_LIMIT_BURST", "2")
    monkeypatch.setenv("COG_TRUST_PROXY_HEADERS", "true")
    monkeypatch.setenv("COG_TRUSTED_PROXY_HEADER", "X-Forwarded-For")

    importlib.reload(config)
    monkeypatch.setattr(
        config,
        "settings",
        config.Settings(
            api_key="key-1,key-2,key-3",
            rate_limit_rps=0.0,
            rate_limit_burst=2,
            trust_proxy_headers=True,
            trusted_proxy_header="X-Forwarded-For",
        ),
    )
    monkeypatch.setattr(auth, "settings", config.settings)
    importlib.reload(rate_limit)
    monkeypatch.setattr(rate_limit, "RedisBucketLimiter", DummyLimiter)
    importlib.reload(main)

    client = TestClient(main.app)

    forwarded_ips = ["8.8.8.8", "1.1.1.1", "9.9.9.9"]
    for idx, ip in enumerate(forwarded_ips, start=1):
        headers = {"X-API-Key": f"key-{idx}", "X-Forwarded-For": ip}
        assert client.get("/api/health", headers=headers).status_code == 200


@pytest.mark.integration
def test_rate_limit_recovers_from_transient_redis_failure(monkeypatch):
    monkeypatch.setenv("COG_API_KEY", "rate-limit-key")
    monkeypatch.setenv("COG_RATE_LIMIT_RPS", "0")
    monkeypatch.setenv("COG_RATE_LIMIT_BURST", "1")

    importlib.reload(config)
    monkeypatch.setattr(
        config,
        "settings",
        config.Settings(api_key="rate-limit-key", rate_limit_rps=0.0, rate_limit_burst=1),
    )
    monkeypatch.setattr(auth, "settings", config.settings)
    importlib.reload(rate_limit)

    class FailingRedisLimiter:
        def __init__(self, *args, **kwargs):
            pass

        def allow(self, token: str, needed: float = 1.0) -> bool:
            raise RateLimiterUnavailableError("redis unavailable")

    monkeypatch.setattr(rate_limit, "RedisBucketLimiter", FailingRedisLimiter)
    importlib.reload(main)

    client = TestClient(main.app)
    headers = {"X-API-Key": "rate-limit-key"}

    # First call succeeds despite redis outage, swapping the limiter to in-memory storage.
    assert client.get("/api/health", headers=headers).status_code == 200
    # Subsequent requests are throttled by the in-memory limiter.
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


def test_redis_limiter_logs_redacted_token(monkeypatch, caplog):
    token = "super-secret-token"
    token_digest = hashlib.sha256(token.encode("utf-8")).hexdigest()[:12]

    class FakeRedisClient:
        def script_load(self, script: str):  # pragma: no cover - simple stub
            return "sha"

        def evalsha(self, sha: str, num_keys: int, *args):
            raise RuntimeError("redis boom")

    fake_redis_module = SimpleNamespace(from_url=lambda *args, **kwargs: FakeRedisClient())

    monkeypatch.setattr(core_rate_limiter, "redis", fake_redis_module)

    limiter = core_rate_limiter.RedisBucketLimiter(redis_url="redis://fake", bucket_key="test")

    with caplog.at_level(logging.WARNING, logger=core_rate_limiter.logger.name):
        with pytest.raises(core_rate_limiter.RateLimiterUnavailableError):
            limiter.allow(token)

    assert caplog.records, "expected a warning log entry"
    message = caplog.records[0].getMessage()
    assert token not in message
    assert token_digest in message
