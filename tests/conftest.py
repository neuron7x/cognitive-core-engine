import importlib
import os
import uuid
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:  # pragma: no cover - only for type hints
    from fastapi.testclient import TestClient as _TestClient

fastapi_testclient = pytest.importorskip("fastapi.testclient")
TestClient = fastapi_testclient.TestClient

config = importlib.import_module("cognitive_core.config")
auth = importlib.import_module("cognitive_core.api.auth")
main = importlib.import_module("cognitive_core.api.main")
app = main.app


@pytest.fixture(scope="function")
def api_client(monkeypatch):
    api_key = os.environ.get("COG_TEST_API_KEY", f"test-{uuid.uuid4()}")
    monkeypatch.setenv("COG_API_KEY", api_key)
    config.settings = config.Settings(api_key=api_key)
    auth.settings = config.settings
    client = TestClient(app)
    client.headers.update({"X-API-Key": api_key})
    return client
