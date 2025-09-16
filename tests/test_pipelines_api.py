def test_get_pipeline(api_client):
    assert api_client.get("/api/v1/pipelines/sample").json()["id"] == "sample"


def test_run_pipeline(api_client):
    resp = api_client.post("/api/v1/pipelines/run", json={"pipeline_id": "sample"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "completed"
    assert data["artifacts"] == ["result"]


def test_aots_debate_missing_role_returns_404(api_client):
    resp = api_client.post(
        "/api/pipelines/aots_debate",
        json={"prompt": "test", "roles": ["does-not-exist"]},
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == (
        "Role definition 'does-not-exist' not found in agents configuration directory."
    )
