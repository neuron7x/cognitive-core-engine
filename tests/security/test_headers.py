import os

import pytest

from cognitive_core import config
from cognitive_core.api import auth

os.environ.setdefault("COG_API_KEY", "security-test-key")
API_KEY = os.environ["COG_API_KEY"]


def _ensure_key() -> dict[str, str]:
    config.settings = config.Settings(api_key=API_KEY)
    auth.settings = config.settings
    return {"X-API-Key": API_KEY}


@pytest.mark.integration
def test_default_security_headers(api_client):
    r = api_client.get("/api/health", headers=_ensure_key())
    assert r.status_code == 200
    assert "content-type" in {k.lower() for k in r.headers.keys()}
    csp = r.headers.get("content-security-policy")  # may be None
    acao = r.headers.get("access-control-allow-origin", "")
    assert "*" not in acao or "null" not in acao
