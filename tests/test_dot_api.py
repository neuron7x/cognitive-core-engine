def test_dot(api_client):
    response = api_client.post("/api/dot", json={"a": [1, 2, 3], "b": [4, 5, 6]})

    assert response.status_code == 200
    assert response.json()["result"] == 32.0
