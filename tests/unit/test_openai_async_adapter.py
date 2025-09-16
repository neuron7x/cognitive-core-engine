import asyncio

import pytest

from cognitive_core.llm.provider_async import OpenAIAsyncAdapter


def test_openai_async_adapter_rejects_unapproved_base(monkeypatch):
    monkeypatch.setenv("OPENAI_API_BASE", "https://malicious.example.com/v1")
    adapter = OpenAIAsyncAdapter(key="test-key")

    with pytest.raises(RuntimeError):
        asyncio.run(adapter.run("unsafe prompt"))
