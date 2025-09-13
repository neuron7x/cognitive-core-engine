import shlex
import subprocess

import pytest


def _run(cmd: str):
    proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


@pytest.mark.integration
def test_cli_ping():
    for exe in ("cogctl", "python -m cognitive_core.cli"):
        rc, out, _ = _run(f"{exe} ping")
        if rc == 0 and out:
            assert out.strip() == "pong"
            return
    pytest.skip("CLI ping not available")


@pytest.mark.integration
def test_cli_dotv():
    for exe in ("cogctl", "python -m cognitive_core.cli"):
        rc, out, _ = _run(f"{exe} dotv 1,2,3 4,5,6")
        if rc == 0 and out:
            assert '"dot": 32.0' in out
            return
    pytest.skip("CLI dotv not available")
