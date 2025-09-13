def test_solve(api_client):
    js = api_client.post(
        "/api/solve2x2", json={"a": 1, "b": 1, "c": 2, "d": -1, "e": 4, "f": 0}
    ).json()
    assert abs(1 * js["x"] + 1 * js["y"] - 4) < 1e-6


def test_missing_field(api_client):
    r = api_client.post("/api/solve2x2", json={"a": 1})
    assert r.status_code == 422
