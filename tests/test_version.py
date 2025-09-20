from __future__ import annotations

import re
from importlib import metadata as importlib_metadata
from pathlib import Path

import pytest

import cognitive_core
from cognitive_core import cli


def _read_pyproject_version() -> str:
    root = Path(__file__).resolve().parents[1]
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"(?P<version>[^"]+)"', pyproject, re.MULTILINE)
    assert match, "pyproject.toml is missing a [project] version field"
    return match.group("version")


def test_package_version_matches_pyproject() -> None:
    expected = _read_pyproject_version()
    assert cognitive_core.__version__ == expected

    try:
        dist_version = importlib_metadata.version("cognitive-core-engine")
    except importlib_metadata.PackageNotFoundError:
        dist_version = None

    if dist_version is not None:
        assert dist_version == expected


def test_cli_version_flag_reports_expected_value(capsys: pytest.CaptureFixture[str]) -> None:
    expected = _read_pyproject_version()
    parser = cli.build_parser()

    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--version"])

    assert exc.value.code == 0
    out, err = capsys.readouterr()
    assert err == ""
    assert expected in out
