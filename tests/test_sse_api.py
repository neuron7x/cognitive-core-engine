import pytest


@pytest.mark.integration
def test_sse_events(api_client):
    r = api_client.get("/api/events/sse", stream=True)
    assert r.status_code in (200, 204)
    ctype = r.headers.get("content-type", "")
    assert "text/event-stream" in ctype
