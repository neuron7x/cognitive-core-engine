def test_get_pipeline(api_client):
    assert api_client.get("/api/v1/pipelines/sample").json()["id"] == "sample"


def test_run_pipeline(api_client):
    resp = api_client.post("/api/v1/pipelines/run", json={"pipeline_id": "sample"})
    data = resp.json()
    assert data["status"] == "completed"
    assert data["artifacts"] == ["result"]
