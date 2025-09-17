import pytest

import cognitive_core.llm.provider_wrapper as provider_wrapper


class CostlyProvider(provider_wrapper.MockProvider):
    def run(self, prompt: str, **kwargs) -> dict:
        return {"text": prompt.upper(), "_cost_usd": 0.5}


def test_provider_wrapper_falls_back_to_in_memory_rate_limits(monkeypatch):
    monkeypatch.setenv("REDIS_URL", "redis://example.com:6379/0")
    monkeypatch.setattr(provider_wrapper.settings, "rate_limit_burst", 1, raising=False)
    monkeypatch.setattr(provider_wrapper.settings, "rate_limit_rps", 0.0, raising=False)

    class FailingLimiter:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("redis connection failed")

    class FailingCostTracker:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("redis connection failed")

    monkeypatch.setattr(provider_wrapper, "RedisBucketLimiter", FailingLimiter)
    monkeypatch.setattr(provider_wrapper, "RedisCostTracker", FailingCostTracker)

    wrapper = provider_wrapper.ProviderWrapper(CostlyProvider())

    assert isinstance(wrapper.limiter, provider_wrapper.InMemoryBucketLimiter)
    assert isinstance(wrapper.tracker, provider_wrapper.InMemoryCostTracker)

    first = wrapper.run("hello", client_id="client")
    second = wrapper.run("world", client_id="client")

    assert first["_cost_accum"] == pytest.approx(0.5)
    assert wrapper.tracker.get_cost("client") == pytest.approx(0.5)
    assert second["error"] == "rate_limited"
