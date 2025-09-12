from fastapi.testclient import TestClient
from cognitive_core.api.main import app

client = TestClient(app)

def test_contract_health_shape():
    r = client.get("/api/health")
    assert r.status_code == 200
    j = r.json()
    assert set(j.keys()) == {"status"} and j["status"] == "ok"

def test_contract_dot_shape():
    r = client.post("/api/dot", json={"a":[1,2,3], "b":[4,5,6]})
    assert r.status_code == 200
    j = r.json()
    assert "result" in j and isinstance(j["result"], (int,float))

def test_contract_solve2x2_shape():
    r = client.post("/api/solve2x2", json={"a11":1,"a12":2,"a21":3,"a22":4,"b1":5,"b2":6})
    assert r.status_code == 200
    j = r.json()
    assert "x" in j and "y" in j
