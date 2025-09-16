from __future__ import annotations

import os
from urllib.parse import urlparse, urlunparse

from .costs import compute_cost_from_usage

try:  # pragma: no cover - runtime optional dependency
    import requests
except Exception:  # pragma: no cover - when requests is missing
    requests = None


class LLMProvider:
    def run(self, prompt: str, **kw) -> dict:
        raise NotImplementedError


class MockProvider(LLMProvider):
    name = "mock"

    def run(self, prompt: str, **kw):
        return {"text": f"<mock response: {prompt[:200]}>", "_cost_usd": 0.0}


class OpenAIAdapter(LLMProvider):
    name = "openai"

    _ALLOWED_API_HOSTS = {"api.openai.com"}

    def __init__(self, key: str | None = None, model: str = "gpt-4o-mini"):
        self.key = key or os.environ.get("OPENAI_API_KEY")
        self.model = model

    @classmethod
    def _validate_and_normalize_api_base(cls, base: str) -> str:
        parsed = urlparse(base)
        if parsed.scheme.lower() != "https" or not parsed.netloc or not parsed.hostname:
            raise RuntimeError("OPENAI_API_BASE must be an https URL with a valid hostname.")

        hostname = parsed.hostname.lower()
        allowed_hosts = {host.lower() for host in cls._ALLOWED_API_HOSTS}
        if hostname not in allowed_hosts:
            raise RuntimeError(
                "OPENAI_API_BASE hostname is not allowed."
            )

        sanitized = urlunparse(
            ("https", parsed.netloc, parsed.path or "", "", "", "")
        ).rstrip("/")

        return sanitized or f"https://{parsed.netloc}"

    def run(self, prompt: str, **kwargs) -> dict:
        # Live implementation using requests. Requires 'requests' package and network access.
        if not self.key:
            raise RuntimeError("OpenAIAdapter requires OPENAI_API_KEY in environment.")

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = {
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }
        base = self._validate_and_normalize_api_base(
            os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
        )
        url = f"{base}/chat/completions"

        if requests is None:
            raise RuntimeError(
                "requests package not installed. Install 'requests' to enable OpenAIAdapter."
            )

        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        jr = r.json()

        text = ""
        if isinstance(jr, dict) and "choices" in jr and len(jr["choices"]) > 0:
            ch = jr["choices"][0]
            if isinstance(ch.get("message"), dict):
                text = ch.get("message", {}).get("content") or ch.get("text") or ""
            else:
                text = ch.get("text") or ""

        usage = jr.get("usage") if isinstance(jr, dict) else None

        cost = 0.0
        try:
            if (
                os.environ.get("ENABLE_COST_CALC", "false").lower() in ("1", "true", "yes")
                and usage
            ):
                cost = compute_cost_from_usage(self.model, usage)
        except Exception:
            cost = 0.0

        return {"text": text, "_cost_usd": cost, "_usage": usage, "_raw": jr}


# Provider wrapper will be added by rate_limiter integration
def get_provider():
    name = os.environ.get("LLM_PROVIDER", "mock")
    if name == "openai":
        return OpenAIAdapter()
    return MockProvider()
