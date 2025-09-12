# ruff: noqa: I001
import importlib.util
import pathlib
import tomllib

ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_repo_has_core_files():
    assert (ROOT / "pyproject.toml").exists()
    assert (ROOT / "README.md").exists()
    assert (ROOT / ".github" / "workflows" / "ci.yml").exists()


def test_pyproject_is_valid_toml():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert "project" in data and "name" in data["project"]


def test_optional_package_import():
    spec = importlib.util.find_spec("cognitive_core")
    if spec is not None:
        __import__("cognitive_core")
