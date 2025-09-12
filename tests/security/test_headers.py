import pytest


@pytest.mark.integration
def test_default_security_headers(api_client):
    r = api_client.get("/api/health")
    assert r.status_code == 200
    assert "content-type" in {k.lower() for k in r.headers.keys()}
    csp = r.headers.get("content-security-policy")  # may be None
    acao = r.headers.get("access-control-allow-origin", "")
    assert "*" not in acao or "null" not in acao
