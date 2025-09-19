def test_healthz(api_client):
    resp = api_client.get("/api/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_livez(api_client):
    resp = api_client.get("/api/livez")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_readyz(api_client):
    resp = api_client.get("/api/readyz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_info(api_client):
    resp = api_client.get("/api/v1/info")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"]
    assert data["version"]
