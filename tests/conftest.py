import importlib
import pkgutil
from typing import Optional

import pytest

# Якщо FastAPI відсутній локально — ввічливо скіпаємо інтеграційні тести
try:
    import fastapi  # noqa: F401
    from fastapi.testclient import TestClient  # type: ignore
except Exception:  # pragma: no cover
    pytest.skip("fastapi[test] not installed; skipping API tests", allow_module_level=True)
    TestClient = None  # type: ignore


def _find_fastapi_app() -> Optional[object]:
    """Heuristic search for a FastAPI app inside `cognitive_core` package."""
    try:
        pkg = importlib.import_module("cognitive_core")
    except Exception:
        return None

    candidates = [
        "cognitive_core.api",
        "cognitive_core.app",
        "cognitive_core.main",
        "cognitive_core.server",
    ]
    for mod_name in candidates:
        try:
            mod = importlib.import_module(mod_name)
            app = getattr(mod, "app", None) or getattr(mod, "api", None)
            if app and app.__class__.__name__ in {"FastAPI", "Starlette"}:
                return app
        except Exception:
            pass

    # deep scan; ігноруємо модулі, що не імпортуються
    try:
        for m in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
            try:
                mod = importlib.import_module(m.name)
                for name in ("app", "api", "api_app"):
                    app = getattr(mod, name, None)
                    if app and app.__class__.__name__ in {"FastAPI", "Starlette"}:
                        return app
            except Exception:
                continue
    except Exception:
        pass
    return None


@pytest.fixture(scope="session")
def api_client():
    app = _find_fastapi_app()
    if app is None:
        pytest.skip("FastAPI app not found in cognitive_core")
    return TestClient(app)
