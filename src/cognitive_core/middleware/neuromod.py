from pydantic import BaseModel
from fastapi import Request

class NeuromodState(BaseModel):
    arousal: float = 0.5
    uncertainty: float = 0.2
    novelty: float = 0.1

def policy(s: NeuromodState) -> dict:
    return {
        "temperature": 0.7 + 0.6*s.uncertainty,
        "rate_mult": max(0.5, 1.0 - 0.5*s.arousal),
        "cache_ttl": int(30 + 120*s.novelty),
    }

async def neuromod_middleware(request: Request, call_next):
    q = getattr(request.app.state, "queue_depth", 0)
    s = NeuromodState(arousal=min(1.0, q/100.0))
    request.state.cog_policy = policy(s)
    resp = await call_next(request)
    resp.headers["X-Cog-Policy"] = str(request.state.cog_policy)
    return resp
