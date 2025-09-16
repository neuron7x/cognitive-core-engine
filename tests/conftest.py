import os
import uuid

import pytest

try:
    from fastapi.testclient import TestClient  # type: ignore
except Exception:
    pytest.skip("fastapi[test] not installed; skipping API tests", allow_module_level=True)

from cognitive_core import config
from cognitive_core.api import auth
from cognitive_core.api.main import app

@pytest.fixture(scope="function")
def api_client(monkeypatch):
    api_key = os.environ.get("COG_TEST_API_KEY", f"test-{uuid.uuid4()}" )
    monkeypatch.setenv("COG_API_KEY", api_key)
    config.settings = config.Settings(api_key=api_key)
    auth.settings = config.settings
    client = TestClient(app)
    client.headers.update({"X-API-Key": api_key})
    return client
