import asyncio

import pytest

from cognitive_core.llm.provider_async import OpenAIAsyncAdapter


def test_openai_async_adapter_rejects_unapproved_api_base(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_API_BASE", "https://evil.example.com/v1")

    adapter = OpenAIAsyncAdapter()

    with pytest.raises(RuntimeError):
        asyncio.run(adapter.run("hello"))
