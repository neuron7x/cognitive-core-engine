from __future__ import annotations

import re
from importlib import metadata as importlib_metadata
from pathlib import Path


def _read_version_from_pyproject() -> str:
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    if pyproject_path.is_file():
        text = pyproject_path.read_text(encoding="utf-8")
        match = re.search(r'^version\s*=\s*"(?P<version>[^"]+)"', text, re.MULTILINE)
        if match:
            return match.group("version")
    raise RuntimeError("Unable to determine package version from pyproject.toml")


def _discover_version() -> str:
    try:
        return importlib_metadata.version("cognitive-core-engine")
    except importlib_metadata.PackageNotFoundError:
        return _read_version_from_pyproject()


__version__ = _discover_version()

__all__ = ["__version__"]
