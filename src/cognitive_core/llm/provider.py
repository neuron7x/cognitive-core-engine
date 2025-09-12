
from __future__ import annotations
import os
class LLMProvider:
    def run(self, prompt: str, **kw) -> dict: raise NotImplementedError

class MockProvider(LLMProvider):
    name = "mock"
    def run(self, prompt: str, **kw):
        return {"text": f"<mock response: {prompt[:200]}>", "_cost_usd": 0.0}

class OpenAIAdapter(LLMProvider):
    name = "openai"
    def __init__(self, key=None, model: str = "gpt-4o-mini"):
        import os
        self.key = key or os.environ.get("OPENAI_API_KEY")
        self.model = model

    def run(self, prompt: str, **kwargs) -> dict:
        # Live implementation using requests. Requires 'requests' package and network access.
        import os, json
from .costs import compute_cost_from_usage
        if not self.key:
            raise RuntimeError("OpenAIAdapter requires OPENAI_API_KEY in environment.")
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}]
        }
        headers = {
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json"
        }
        base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
        url = f"{base}/chat/completions"
        try:
            import requests
        except Exception as e:
            raise RuntimeError("requests package not installed. Install 'requests' to enable OpenAIAdapter.")
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        jr = r.json()
        text = ""
        if isinstance(jr, dict) and "choices" in jr and len(jr["choices"])>0:
            ch = jr["choices"][0]
            if isinstance(ch.get("message"), dict):
                text = ch.get("message", {}).get("content") or ch.get("text") or ""
            else:
                text = ch.get("text") or ""
        cost = 0.0
        try:
            if os.environ.get('ENABLE_COST_CALC','false').lower() in ('1','true','yes') and usage:
                cost = compute_cost_from_usage(self.model, usage)
        except Exception:
            cost = 0.0
        usage = jr.get('usage') if isinstance(jr, dict) else None
        return {"text": text, "_cost_usd": cost, "_usage": usage, "_raw": jr}

# Provider wrapper will be added by rate_limiter integration
def get_provider():
    name = os.environ.get("LLM_PROVIDER", "mock")
    if name == "openai":
        return OpenAIAdapter()
    return MockProvider()
