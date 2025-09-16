import pytest

from cognitive_core.llm import provider as provider_module
from cognitive_core.llm.costs import compute_cost_from_usage
from cognitive_core.llm.provider import OpenAIAdapter


def test_cost_computation_with_usage(monkeypatch):
    usage = {"prompt_tokens": 10, "completion_tokens": 20}

    class DummyResponse:
        def json(self):
            return {
                "choices": [{"message": {"content": "ok"}}],
                "usage": usage,
            }

        def raise_for_status(self):
            pass

    class DummyRequests:
        @staticmethod
        def post(url, headers, json, timeout):
            return DummyResponse()

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("ENABLE_COST_CALC", "true")
    monkeypatch.setattr(provider_module, "requests", DummyRequests)

    adapter = OpenAIAdapter()
    result = adapter.run("hello")

    expected = compute_cost_from_usage(adapter.model, usage)
    assert result["_cost_usd"] == expected
    assert result["_usage"] == usage


def test_openai_adapter_rejects_unapproved_api_base(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_API_BASE", "https://evil.example.com/v1")

    adapter = OpenAIAdapter()

    with pytest.raises(RuntimeError):
        adapter.run("hello")
