import pytest


@pytest.mark.integration
def test_dot_api(api_client):
    payload = {"a": [1, 2, 3], "b": [4, 5, 6]}
    r = api_client.post("/api/dot", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data.get("dot") in (32, 32.0)
