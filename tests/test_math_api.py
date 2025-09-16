def test_dot_mismatched_lengths(api_client):
    response = api_client.post(
        "/api/math/dot",
        json={"a": [1.0, 2.0], "b": [3.0]},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Vectors must be the same length"}
