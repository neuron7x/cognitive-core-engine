import pathlib
import pytest

pytest.importorskip("yaml", reason="pyyaml not installed; skipping repo tests")
import yaml

y = yaml.safe_load(open(".github/workflows/ci.yml", "r", encoding="utf-8"))
assert "jobs" in y
