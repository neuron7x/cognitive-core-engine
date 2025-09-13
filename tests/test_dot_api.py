import pytest


def test_dot(api_client):
    assert (
        api_client.post("/api/dot", json={"a": [1, 2, 3], "b": [4, 5, 6]}).json()["dot"]
        == 32.0
    )


@pytest.mark.parametrize(
    "payload",
    [
        {"a": [1, 2]},  # missing b
        {"a": [1, 2], "b": [3, "x"]},  # non-numeric value
    ],
)
def test_dot_validation_errors(api_client, payload):
    assert api_client.post("/api/dot", json=payload).status_code == 422
