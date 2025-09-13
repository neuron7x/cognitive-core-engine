import pytest


def test_solve(api_client):
    js = api_client.post(
        "/api/solve2x2", json={"a": 1, "b": 1, "c": 2, "d": -1, "e": 4, "f": 0}
    ).json()
    assert abs(1 * js["x"] + 1 * js["y"] - 4) < 1e-6


@pytest.mark.parametrize(
    "payload",
    [
        {"a": 1, "b": 1, "c": 2, "d": -1, "e": 4},  # missing f
        {"a": "bad", "b": 1, "c": 2, "d": -1, "e": 4, "f": 0},  # non-numeric a
    ],
)
def test_solve_validation_errors(api_client, payload):
    assert api_client.post("/api/solve2x2", json=payload).status_code == 422
