import pytest

try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
except Exception:  # pragma: no cover - allow running without fastapi installed
    pytest.skip("fastapi not installed; skipping rate limit tests", allow_module_level=True)

import cognitive_core.api.rate_limit as rate_limit
from cognitive_core.api.rate_limit import InMemoryBucketLimiter, RateLimitMiddleware
from cognitive_core.config import settings
from starlette.requests import Request


def test_rate_limit_falls_back_to_in_memory(monkeypatch, caplog):
    class FailingLimiter:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("redis missing")

    monkeypatch.setattr(
        "cognitive_core.api.rate_limit.RedisBucketLimiter", FailingLimiter
    )

    app = FastAPI()
    with caplog.at_level("WARNING"):
        middleware = RateLimitMiddleware(app)

    assert middleware.limiter.__class__.__name__ == "InMemoryBucketLimiter"
    assert any("falling back to in-memory limiter" in message for message in caplog.messages)


def test_rate_limit_logs_when_redis_dependency_missing(monkeypatch, caplog):
    monkeypatch.setattr(
        "cognitive_core.api.rate_limit.RedisBucketLimiter", None, raising=False
    )
    monkeypatch.setattr(
        "cognitive_core.api.rate_limit._redis_import_error",
        RuntimeError("redis package unavailable"),
        raising=False,
    )

    app = FastAPI()

    with caplog.at_level("WARNING"):
        middleware = RateLimitMiddleware(app)

    assert middleware.limiter.__class__.__name__ == "InMemoryBucketLimiter"
    assert any("redis package unavailable" in message for message in caplog.messages)


def test_in_memory_rate_limiter_enforces_limits(monkeypatch):
    class FailingLimiter:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("redis missing")

    monkeypatch.setattr(
        "cognitive_core.api.rate_limit.RedisBucketLimiter", FailingLimiter
    )
    monkeypatch.setattr(settings, "rate_limit_burst", 1)
    monkeypatch.setattr(settings, "rate_limit_rps", 0.0)
    monkeypatch.setattr(rate_limit, "settings", settings)

    app = FastAPI()
    app.add_middleware(RateLimitMiddleware)

    @app.get("/api/test")
    def read() -> dict[str, bool]:
        return {"ok": True}

    with TestClient(app) as client:
        headers = {"X-API-Key": "fallback"}
        first = client.get("/api/test", headers=headers)
        second = client.get("/api/test", headers=headers)

    assert first.status_code == 200
    assert second.status_code == 429


def test_resolve_client_host_prefers_first_global_ip_from_proxy(monkeypatch):
    monkeypatch.setattr(rate_limit, "RedisBucketLimiter", InMemoryBucketLimiter)
    monkeypatch.setattr(settings, "trust_proxy_headers", True)
    monkeypatch.setattr(settings, "trusted_proxy_header", "X-Forwarded-For")
    monkeypatch.setattr(rate_limit, "settings", settings)

    middleware = RateLimitMiddleware(FastAPI())

    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "path": "/api/test",
        "raw_path": b"/api/test",
        "scheme": "http",
        "root_path": "",
        "headers": [
            (b"x-forwarded-for", b"127.0.0.1, 10.0.0.5,  8.8.8.8   ,1.1.1.1"),
        ],
        "client": ("192.0.2.10", 12345),
        "server": ("testserver", 80),
        "query_string": b"",
    }

    request = Request(scope)

    assert middleware._resolve_client_host(request) == "8.8.8.8"
