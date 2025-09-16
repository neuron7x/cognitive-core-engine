import pytest

try:  # pragma: no cover - optional dependency
    import yaml
except ModuleNotFoundError:  # pragma: no cover - skip if PyYAML unavailable
    pytest.skip("pyyaml is not installed", allow_module_level=True)

y = yaml.safe_load(open(".github/workflows/ci.yml", "r", encoding="utf-8"))
assert "jobs" in y
