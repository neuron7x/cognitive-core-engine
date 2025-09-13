def test_dot(api_client):
    assert (
        api_client.post("/api/dot", json={"a": [1, 2, 3], "b": [4, 5, 6]}).json()["result"]
        == 32.0
    )
