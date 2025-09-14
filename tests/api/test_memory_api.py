import uuid


def test_memory_upsert_and_query_roundtrip(client, auth_headers):
    k = f"test/session/{uuid.uuid4()}"
    up = {"key": k, "payload": {"x": 1, "txt": "hello"}, "reward": 0.5, "surprise": 0.2}
    r = client.post("/api/memory/upsert", json=up, headers=auth_headers)
    assert r.status_code in (200, 201)
    data = r.json()
    assert ("ok" in data and data["ok"]) or ("id" in data)
    q = {"key": k, "limit": 10}
    rq = client.post("/api/memory/query", json=q, headers=auth_headers)
    assert rq.status_code == 200
    out = rq.json()
    items = out.get("items") if isinstance(out, dict) else out
    if items is None:
        items = out.get("data")
    assert isinstance(items, list)
    assert any(it.get("key") == k for it in items)


def test_memory_requires_api_key(client):
    k = f"test/session/{uuid.uuid4()}"
    up = {"key": k, "payload": {"x": 2}, "reward": 0.1, "surprise": 0.9}
    r = client.post("/api/memory/upsert", json=up)
    assert r.status_code in (401, 403)
    rq = client.post("/api/memory/query", json={"key": k, "limit": 5})
    assert rq.status_code in (401, 403)


def test_memory_upsert_validation(client, auth_headers):
    r = client.post("/api/memory/upsert", json={}, headers=auth_headers)
    assert r.status_code in (400, 422)


def test_memory_query_limit(client, auth_headers):
    base = f"test/limit/{uuid.uuid4()}"
    for i in range(3):
        client.post(
            "/api/memory/upsert",
            json={"key": base, "payload": {"i": i}, "reward": 0.0, "surprise": 0.0},
            headers=auth_headers,
        )
    rq = client.post("/api/memory/query", json={"key": base, "limit": 1}, headers=auth_headers)
    assert rq.status_code == 200
    out = rq.json()
    items = out.get("items") if isinstance(out, dict) else out
    if items is None:
        items = out.get("data")
    assert isinstance(items, list)
    assert len(items) <= 1
