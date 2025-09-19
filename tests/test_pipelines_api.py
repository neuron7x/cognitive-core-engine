import uuid


def test_list_pipelines_includes_seeded_sample(api_client):
    resp = api_client.get("/api/v1/pipelines")
    assert resp.status_code == 200, resp.text
    pipelines = resp.json()
    assert any(p["name"] == "Sample" for p in pipelines)


def test_create_pipeline_and_fetch(api_client):
    name = f"Pipeline-{uuid.uuid4()}"
    create_resp = api_client.post("/api/v1/pipelines", json={"name": name})
    assert create_resp.status_code == 201, create_resp.text
    pipeline = create_resp.json()
    assert pipeline["name"] == name
    assert pipeline["steps"] == 1

    get_resp = api_client.get(f"/api/v1/pipelines/{pipeline['id']}")
    assert get_resp.status_code == 200, get_resp.text
    fetched = get_resp.json()
    assert fetched == pipeline


def test_run_pipeline_creates_completed_run(api_client):
    name = f"Runnable-{uuid.uuid4()}"
    pipeline_id = api_client.post("/api/v1/pipelines", json={"name": name}).json()["id"]

    run_resp = api_client.post("/api/v1/pipelines/run", json={"pipeline_id": pipeline_id})
    assert run_resp.status_code == 200, run_resp.text
    run_data = run_resp.json()
    assert isinstance(run_data["run_id"], int)
    assert run_data["status"] == "completed"
    assert run_data["artifacts"] == ["result"]


def test_run_pipeline_missing_returns_404(api_client):
    run_resp = api_client.post("/api/v1/pipelines/run", json={"pipeline_id": 9999})
    assert run_resp.status_code == 404
    assert run_resp.json()["detail"] == "Pipeline not found"


def test_aots_debate_missing_role_returns_404(api_client):
    resp = api_client.post(
        "/api/pipelines/aots_debate",
        json={"prompt": "test", "roles": ["does-not-exist"]},
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == (
        "Role definition 'does-not-exist' not found in agents configuration directory."
    )
