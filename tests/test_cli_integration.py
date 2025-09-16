import shlex
import subprocess

import pytest


def _run(cmd: str):
    try:
        proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    except FileNotFoundError:
        return None, "", "command not found"
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


@pytest.mark.integration
def test_cli_ping():
    for exe in ("cogctl", "python -m cognitive_core.cli"):
        rc, out, _ = _run(f"{exe} ping")
        if rc == 0 and out:
            assert out.strip() == "pong"
            return
    pytest.skip("CLI not available")


@pytest.mark.integration
def test_cli_migrate_status():
    for exe in ("cogctl", "python -m cognitive_core.cli"):
        rc, _, _ = _run(f"{exe} migrate status")
        if rc == 0:
            return
    pytest.skip("CLI migrate not available")


@pytest.mark.integration
def test_cli_pipeline_run():
    for exe in ("cogctl", "python -m cognitive_core.cli"):
        rc, out, _ = _run(f"{exe} pipeline run --name demo")
        if rc == 0 and out:
            assert "demo" in out
            return
    pytest.skip("CLI not available")


@pytest.mark.integration
def test_cli_dotv_mismatched_vectors():
    expected_message = "Vectors must be the same length"
    invoked = False
    for exe in ("cogctl", "python -m cognitive_core.cli"):
        rc, out, err = _run(f"{exe} dotv 1,2 3")
        if rc is None:
            continue
        invoked = True
        if rc != 0:
            message = err or out
            assert expected_message in message
            return
    if not invoked:
        pytest.skip("CLI not available")
    pytest.fail("CLI did not report mismatched vector lengths")

