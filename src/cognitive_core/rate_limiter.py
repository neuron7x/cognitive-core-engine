from __future__ import annotations

import hashlib
import logging
import os
import time

try:
    import redis
except Exception:
    redis = None

logger = logging.getLogger(__name__)


class RateLimiterUnavailableError(RuntimeError):
    """Raised when the Redis backend cannot evaluate rate limits."""


LUA_SCRIPT = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_per_sec = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local needed = tonumber(ARGV[4])
local state = redis.call('HMGET', key, 'tokens', 'last_ts')
local tokens = tonumber(state[1]) or capacity
local last_ts = tonumber(state[2]) or now
local delta = now - last_ts
tokens = math.min(capacity, tokens + delta * refill_per_sec)
local allowed = 0
if tokens >= needed then
  tokens = tokens - needed
  allowed = 1
end
redis.call('HMSET', key, 'tokens', tostring(tokens), 'last_ts', tostring(now))
redis.call('EXPIRE', key, 3600)
return {allowed, tostring(tokens)}
"""


def _token_fingerprint(token: str) -> str:
    """Return a stable, non-reversible fingerprint for sensitive tokens.

    The value is truncated to keep log lines compact while still allowing
    operators to correlate repeated failures for the same credential.
    """

    if not token:
        return "<empty-token>"
    return hashlib.sha256(token.encode("utf-8")).hexdigest()[:12]


class RedisBucketLimiter:
    def __init__(
        self,
        redis_url: str | None = None,
        bucket_key: str = "cce_bucket",
        capacity: int = 60,
        refill_per_sec: float = 1.0,
    ):
        self.redis_url = redis_url or os.environ.get("REDIS_URL")
        if not redis:
            raise RuntimeError(
                "redis package not installed. Install 'redis' to use RedisBucketLimiter."
            )
        self.r = redis.from_url(self.redis_url, decode_responses=True)
        self.bucket_key = bucket_key
        self.capacity = float(capacity)
        self.refill_per_sec = float(refill_per_sec)
        try:
            self.sha = self.r.script_load(LUA_SCRIPT)
        except Exception:
            self.sha = None
            self.lua = LUA_SCRIPT

    def allow(self, token: str, needed: float = 1.0) -> bool:
        key = f"{self.bucket_key}:{token}:state"
        now = time.time()
        try:
            if self.sha:
                res = self.r.evalsha(
                    self.sha, 1, key, self.capacity, self.refill_per_sec, now, needed
                )
            else:
                res = self.r.eval(self.lua, 1, key, self.capacity, self.refill_per_sec, now, needed)
            allowed = int(res[0]) == 1
            return allowed
        except Exception as exc:
            token_digest = _token_fingerprint(token)
            logger.warning(
                "Redis rate limiter error for token hash '%s': %s",
                token_digest,
                exc,
                exc_info=True,
            )
            raise RateLimiterUnavailableError("redis rate limiter unavailable") from exc


class RedisCostTracker:
    def __init__(self, redis_url: str | None = None, prefix: str = "cce_cost"):
        self.redis_url = redis_url or os.environ.get("REDIS_URL")
        if not redis:
            raise RuntimeError(
                "redis package not installed. Install 'redis' to use RedisCostTracker."
            )
        self.r = redis.from_url(self.redis_url, decode_responses=True)
        self.prefix = prefix

    def add_cost(self, key: str, amount: float):
        k = f"{self.prefix}:{key}:total"
        self.r.incrbyfloat(k, float(amount))

    def get_cost(self, key: str) -> float:
        k = f"{self.prefix}:{key}:total"
        v = self.r.get(k)
        return float(v) if v else 0.0
