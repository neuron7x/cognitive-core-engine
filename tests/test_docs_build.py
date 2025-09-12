import shutil
import subprocess

import pytest


def test_mkdocs_build():
    if shutil.which("mkdocs") is None:
        pytest.skip("mkdocs not installed")
    proc = subprocess.run(["mkdocs", "--version"], capture_output=True, text=True)
    assert proc.returncode == 0
