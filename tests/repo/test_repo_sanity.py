import importlib.util as importlib_util
import os
import pathlib
import sys

import tomllib  # Py3.11+

ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_repo_has_core_files():
    assert (ROOT / "pyproject.toml").exists()
    assert (ROOT / "README.md").exists()
    assert (ROOT / ".github" / "workflows" / "ci.yml").exists()


def test_pyproject_is_valid_toml():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert "project" in data and "name" in data["project"]


def test_optional_package_import():
    # Не вимагаємо наявності пакета, але якщо є — він імпортується
    for pkg in ("cognitive_core",):
        spec = importlib_util.find_spec(pkg)
        if spec is not None:
            __import__(pkg)
