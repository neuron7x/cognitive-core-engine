from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[2]


def test_core():
    assert (ROOT / "pyproject.toml").exists() and (ROOT / ".github/workflows/ci.yml").exists()


def test_toml():
    d = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert "project" in d
