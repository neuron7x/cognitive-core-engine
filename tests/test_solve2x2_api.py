import pytest


@pytest.mark.parametrize(
    "payload",
    [
        {"a": 1, "b": 1, "c": 2, "d": -1, "e": 4, "f": 0},
        {"a11": 1, "a12": 1, "a21": 2, "a22": -1, "b1": 4, "b2": 0},
    ],
)
def test_solve(api_client, payload):
    js = api_client.post("/api/solve2x2", json=payload).json()
    assert 1 * js["x"] + 1 * js["y"] == pytest.approx(4)
    assert 2 * js["x"] - 1 * js["y"] == pytest.approx(0)
