import pytest

try:
    from fastapi.testclient import TestClient  # type: ignore
except Exception:
    pytest.skip("fastapi[test] not installed; skipping API tests", allow_module_level=True)
from cognitive_core.api import app


@pytest.fixture(scope="session")
def api_client():
    return TestClient(app)
