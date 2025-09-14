
def test_isr_run(api_client):
    resp = api_client.post("/api/pipelines/isr_run", json={"text": "hello"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert data["output"] == "hello -> R -> I -> P -> Omega"
    assert [a["name"] for a in data["artifacts"]] == ["r", "i", "p", "omega"]
