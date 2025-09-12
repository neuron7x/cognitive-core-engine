import pytest


@pytest.mark.integration
def test_solve2x2_api(api_client):
    payload = {"a": 1, "b": 1, "c": 2, "d": -1, "e": 4, "f": 0}
    r = api_client.post("/api/solve2x2", json=payload)
    assert r.status_code == 200
    data = r.json()
    x, y = data.get("x"), data.get("y")
    assert x is not None and y is not None
    assert abs((1 * x + 1 * y) - 4) < 1e-6
    assert abs((2 * x - 1 * y) - 0) < 1e-6
