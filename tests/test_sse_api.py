def test_sse(api_client):
    r = api_client.get("/api/events/sse", stream=True)
    assert "text/event-stream" in r.headers.get("content-type", "")
