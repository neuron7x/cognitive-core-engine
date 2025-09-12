from __future__ import annotations

import os

try:
    import httpx
except Exception:
    httpx = None


class OpenAIAsyncAdapter:
    name = "openai-async"

    def __init__(self, key: str | None = None, model: str = "gpt-4o-mini"):
        self.key = key or os.environ.get("OPENAI_API_KEY")
        self.model = model

    async def run(self, prompt: str, **kwargs) -> dict:
        if not self.key:
            raise RuntimeError("OpenAIAsyncAdapter requires OPENAI_API_KEY in environment.")
        base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
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
