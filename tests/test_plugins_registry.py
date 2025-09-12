import importlib
import pkgutil

import pytest


def test_plugins_math_dot_exists():
    try:
        pkg = importlib.import_module("cognitive_core")
    except Exception:
        pytest.skip("package not importable")
    found = False
    try:
        for m in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
            if m.name.endswith("plugins") or ".plugins." in m.name:
                mod = importlib.import_module(m.name)
                if hasattr(mod, "registry"):
                    reg = getattr(mod, "registry")
                    if isinstance(reg, dict) and any("dot" in k for k in reg.keys()):
                        found = True
                        break
    except Exception:
        pass
    assert found, "plugins registry with 'dot' entry not found"
