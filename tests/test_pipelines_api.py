def test_get_pipeline(api_client):
    assert api_client.get("/api/v1/pipelines/sample").json()["id"] == "sample"


def test_run_pipeline(api_client):
    resp = api_client.post("/api/v1/pipelines/run", json={"pipeline_id": "sample"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "completed"
    assert data["artifacts"] == ["result"]
