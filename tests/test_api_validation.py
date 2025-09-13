from fastapi.testclient import TestClient
from cognitive_core.api import app


def test_dot_validation():
    client = TestClient(app)
    # missing 'a' field
    res = client.post("/api/dot", json={"b": 2})
    assert res.status_code == 422
