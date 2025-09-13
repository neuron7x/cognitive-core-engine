import pytest


@pytest.fixture(scope="session")
def api_client():
    pytest.importorskip(
        "fastapi", reason="fastapi[test] not installed; skipping API tests"
    )
    from fastapi.testclient import TestClient  # type: ignore
    from cognitive_core.api.main import app

    return TestClient(app)
