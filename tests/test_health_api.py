def test_health(api_client):
    assert api_client.get("/api/health").json()["status"] == "ok"
