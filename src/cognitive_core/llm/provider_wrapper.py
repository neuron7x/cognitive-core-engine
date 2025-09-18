from __future__ import annotations

import logging
import os

from ..api.rate_limit import InMemoryBucketLimiter, InMemoryCostTracker
from ..config import settings
from ..rate_limiter import (
    RateLimiterUnavailableError,
    RedisBucketLimiter,
    RedisCostTracker,
)
from .provider import LLMProvider, MockProvider, OpenAIAdapter


logger = logging.getLogger(__name__)


class ProviderWrapper:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.calls = 0
        self.tokens = 0
        self.cost_usd = 0.0
        self.redis_url = os.environ.get("REDIS_URL")
        self.limiter = None
        self.tracker = None
        self._limiter_kwargs = {
            "capacity": settings.rate_limit_burst,
            "refill_per_sec": settings.rate_limit_rps,
        }
        if self.redis_url:
            try:
                self.limiter = RedisBucketLimiter(
                    redis_url=self.redis_url,
                    bucket_key="cce_bucket",
                    capacity=self._limiter_kwargs["capacity"],
                    refill_per_sec=self._limiter_kwargs["refill_per_sec"],
                )
                self.tracker = RedisCostTracker(redis_url=self.redis_url)
            except Exception as exc:
                logger.warning(
                    "Redis services unavailable (%s); falling back to in-memory limiter.",
                    exc,
                )
                self._ensure_in_memory_limiter()
        else:
            logger.info(
                "REDIS_URL not configured; using in-memory rate limiter and cost tracker."
            )
            self._ensure_in_memory_limiter()

    def run(self, prompt: str, client_id: str = "default", **kwargs) -> dict:
        est_tokens = max(1, len(prompt) // 4)
        if self.limiter:
            try:
                ok = self.limiter.allow(client_id, needed=1.0)
            except RateLimiterUnavailableError as exc:
                logger.warning(
                    "Redis rate limiter unavailable for provider calls (%s); "
                    "switching to in-memory limiter.",
                    exc,
                )
                self._ensure_in_memory_limiter()
                ok = self.limiter.allow(client_id, needed=1.0) if self.limiter else True
            if not ok:
                return {"error": "rate_limited", "_cost_usd": 0.0}
        self.calls += 1
        self.tokens += est_tokens
        res = self.provider.run(prompt, **kwargs)
        cost = float(res.get("_cost_usd", 0.0) or 0.0)
        self.cost_usd += cost
        if self.tracker:
            try:
                self.tracker.add_cost(client_id, cost)
            except Exception:
                pass
        out = dict(res)
        out.update(
            {"_est_tokens": est_tokens, "_total_calls": self.calls, "_cost_accum": self.cost_usd}
        )
        return out

    def _ensure_in_memory_limiter(self) -> None:
        if isinstance(self.limiter, InMemoryBucketLimiter):
            return
        self.limiter = InMemoryBucketLimiter(**self._limiter_kwargs)
        if not isinstance(self.tracker, InMemoryCostTracker):
            self.tracker = InMemoryCostTracker()
