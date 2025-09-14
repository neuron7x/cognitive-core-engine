import os
import importlib
import pytest
from fastapi.testclient import TestClient

API_KEY = "test-key"

@pytest.fixture(scope="session", autouse=True)
def _env():
    os.environ["COG_API_KEY"] = API_KEY
    os.environ["COG_API_KEYS"] = API_KEY
    os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

def _load_app():
    candidates = [
        "cognitive_core.api.app",
        "cognitive_core.api",
        "cognitive_core.main",
        "app",
    ]
    for name in candidates:
        try:
            mod = importlib.import_module(name)
            app = getattr(mod, "app", None)
            if app is not None:
                return app
        except Exception:
            pass
    raise RuntimeError("FastAPI app not found")

@pytest.fixture(scope="session")
def app():
    return _load_app()

@pytest.fixture(scope="session")
def client(app):
    return TestClient(app)

@pytest.fixture
def auth_headers():
    return {"X-API-Key": API_KEY, "Content-Type": "application/json"}
