import shutil
import subprocess
from pathlib import Path

import pytest


def test_mkdocs_build(tmp_path):
    if shutil.which("mkdocs") is None:
        pytest.skip("mkdocs not installed")
    project_root = Path(__file__).resolve().parent.parent
    site_dir = tmp_path / "site"
    proc = subprocess.run(
        [
            "mkdocs",
            "build",
            "--strict",
            "--site-dir",
            str(site_dir),
        ],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    assert proc.returncode == 0, (
        "mkdocs build failed with exit code"
        f" {proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    )
