from cognitive_core.plugins.attention_router import AttentionRouter

def test_attention_router():
    r = AttentionRouter()
    fast = r.route(type("T", (), {"novelty":1.0,"importance":1.0,"latency_ms":10}))
    slow = r.route(type("T", (), {"novelty":0.0,"importance":0.0,"latency_ms":500}))
    assert fast=="fast_lane"
    assert slow=="defer"
