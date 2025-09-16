import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from cognitive_core.api.auth import verify_api_key
from cognitive_core.api.security import SecureHeadersMiddleware


@pytest.mark.integration
def test_default_security_headers(api_client):
    api_client.app.dependency_overrides[verify_api_key] = lambda: None
    try:
        r = api_client.get("/api/health")
    finally:
        api_client.app.dependency_overrides.pop(verify_api_key, None)
    assert r.status_code == 200
    assert "content-type" in {k.lower() for k in r.headers.keys()}
    csp = r.headers.get("content-security-policy")  # may be None
    acao = r.headers.get("access-control-allow-origin", "")
    assert "*" not in acao or "null" not in acao
    assert r.headers.get("referrer-policy") == "strict-origin-when-cross-origin"
    assert r.headers.get("permissions-policy") == "interest-cohort=()"
    assert csp is None


def test_custom_security_headers():
    app = FastAPI()
    app.add_middleware(
        SecureHeadersMiddleware,
        referrer_policy="no-referrer",
        permissions_policy="geolocation=(self)",
        content_security_policy="default-src 'self'",
    )

    @app.get("/")
    def _root() -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Permissions-Policy"] == "geolocation=(self)"
    assert response.headers["Content-Security-Policy"] == "default-src 'self'"
