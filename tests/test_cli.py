import json
import shlex
import subprocess

import pytest


def _run(cmd: str):
    proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


@pytest.mark.integration
def test_cli_dotv():
    for exe in ("cogctl", "python -m cognitive_core.cli"):
        rc, out, _ = _run(f"{exe} dotv 1,2,3 4,5,6")
        if rc == 0 and out:
            try:
                val = json.loads(out).get("dot", None)
                if val is None:
                    val = float(out)
            except Exception:
                val = float(out)
            assert abs(val - 32.0) < 1e-9
            return
    pytest.skip("CLI not available")


@pytest.mark.integration
def test_cli_solve2x2():
    for exe in ("cogctl", "python -m cognitive_core.cli"):
        rc, out, _ = _run(f"{exe} solve2x2 1 1 2 -1 4 0")
        if rc == 0 and out:
            return
    pytest.skip("CLI not available")
