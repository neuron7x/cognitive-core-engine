def test_healthz(api_client):
    assert api_client.get("/api/healthz").json()["status"] == "ok"


def test_livez(api_client):
    assert api_client.get("/api/livez").json()["status"] == "ok"


def test_readyz(api_client):
    assert api_client.get("/api/readyz").json()["status"] == "ok"


def test_info(api_client):
    data = api_client.get("/api/v1/info").json()
    assert data["name"]
    assert data["version"]
