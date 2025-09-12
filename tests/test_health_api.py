import pytest

@pytest.mark.integration
def test_health(api_client):
    r = api_client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert data.get("status") in {"ok", "healthy", "ready"}
