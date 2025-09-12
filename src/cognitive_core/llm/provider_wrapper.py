
from __future__ import annotations
import os
from .provider import LLMProvider, MockProvider, OpenAIAdapter
class ProviderWrapper:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.calls = 0
        self.tokens = 0
        self.cost_usd = 0.0
        self.redis_url = os.environ.get('REDIS_URL')
        self.limiter = None
        self.tracker = None
        if self.redis_url:
            try:
                from ..rate_limiter import RedisBucketLimiter, RedisCostTracker
                self.limiter = RedisBucketLimiter(redis_url=self.redis_url, bucket_key='cce_bucket')
                self.tracker = RedisCostTracker(redis_url=self.redis_url)
            except Exception:
                self.limiter = None
                self.tracker = None

    def run(self, prompt: str, client_id: str = 'default', **kwargs) -> dict:
        est_tokens = max(1, len(prompt) // 4)
        if self.limiter:
            ok = self.limiter.allow(client_id, needed=1.0)
            if not ok:
                return {'error': 'rate_limited', '_cost_usd': 0.0}
        self.calls += 1
        self.tokens += est_tokens
        res = self.provider.run(prompt, **kwargs)
        cost = float(res.get('_cost_usd', 0.0) or 0.0)
        self.cost_usd += cost
        if self.tracker:
            try:
                self.tracker.add_cost(client_id, cost)
            except Exception:
                pass
        out = dict(res)
        out.update({'_est_tokens': est_tokens, '_total_calls': self.calls, '_cost_accum': self.cost_usd})
        return out
