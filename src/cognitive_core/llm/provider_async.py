from __future__ import annotations

import os
from urllib.parse import urlparse, urlunparse

try:
    import httpx
except Exception:
    httpx = None

from .provider import OpenAIAdapter


class OpenAIAsyncAdapter:
    name = "openai-async"

    _ALLOWED_API_HOSTS = OpenAIAdapter._ALLOWED_API_HOSTS

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
            raise RuntimeError("OPENAI_API_BASE hostname is not allowed.")

        sanitized = urlunparse(("https", parsed.netloc, parsed.path or "", "", "", "")).rstrip("/")
        return sanitized or f"https://{parsed.netloc}"

    async def run(self, prompt: str, **kwargs) -> dict:
        if not self.key:
            raise RuntimeError("OpenAIAsyncAdapter requires OPENAI_API_KEY in environment.")
        base = self._validate_and_normalize_api_base(
            os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
        )
        url = f"{base}/chat/completions"
        payload = {"model": self.model, "messages": [{"role": "user", "content": prompt}]}
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        # Uncomment and ensure httpx is installed to enable live calls.
        # async with httpx.AsyncClient(timeout=30.0) as client:
        #     r = await client.post(url, headers=headers, json=payload)
        #     r.raise_for_status()
        #     jr = r.json()
        #     # parse jr similar to OpenAIAdapter
        return {"text": f"<openai-async suppressed: {prompt[:200]}>", "_cost_usd": 0.0}
