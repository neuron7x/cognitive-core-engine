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
    invoked = False
    errors = []
    for exe in ("cogctl", "python -m cognitive_core.cli"):
        rc, out, err = _run(f"{exe} ping")
        if rc is None:
            continue
        invoked = True
        if rc == 0 and out:
            assert out.strip() == "pong"
            return
        if rc != 0:
            errors.append(f"{exe}: {err or out}")
    if invoked:
        if errors:
            pytest.fail("; ".join(errors))
        pytest.fail("CLI ran but did not return expected output")
    pytest.skip("CLI not available")


@pytest.mark.integration
def test_cli_migrate_status():
    invoked = False
    errors = []
    for exe in ("cogctl", "python -m cognitive_core.cli"):
        rc, _out, err = _run(f"{exe} migrate status")
        if rc is None:
            continue
        invoked = True
        if rc == 0:
            return
        errors.append(f"{exe}: {err}")
    if invoked:
        pytest.fail("; ".join(filter(None, errors)) or "CLI migrate returned unexpected result")
    pytest.skip("CLI migrate not available")


@pytest.mark.integration
def test_cli_pipeline_run():
    invoked = False
    errors = []
    for exe in ("cogctl", "python -m cognitive_core.cli"):
        rc, out, err = _run(f"{exe} pipeline run --name demo")
        if rc is None:
            continue
        invoked = True
        if rc == 0 and out:
            assert "demo" in out
            return
        if rc != 0:
            errors.append(f"{exe}: {err or out}")
    if invoked:
        if errors:
            pytest.fail("; ".join(errors))
        pytest.fail("CLI ran but did not return expected output")
    pytest.skip("CLI not available")


@pytest.mark.integration
def test_cli_pipeline_run_missing_pipeline():
    expected = "Pipeline 'does-not-exist' not found"
    invoked = False
    errors = []
    for exe in ("cogctl", "python -m cognitive_core.cli"):
        rc, out, err = _run(f"{exe} pipeline run --name does-not-exist")
        if rc is None:
            continue
        invoked = True
        if rc and (err or out):
            message = err or out
            assert expected in message
            return
        errors.append(f"{exe}: {err or out}")
    if not invoked:
        pytest.skip("CLI not available")
    pytest.fail("; ".join(errors) or "CLI did not signal missing pipeline")


@pytest.mark.integration
def test_cli_dotv_mismatched_vectors():
    expected_message = "Vectors must be the same length"
    invoked = False
    errors = []
    for exe in ("cogctl", "python -m cognitive_core.cli"):
        rc, out, err = _run(f"{exe} dotv 1,2 3")
        if rc is None:
            continue
        invoked = True
        if rc != 0:
            message = err or out
            assert expected_message in message
            return
        errors.append(f"{exe}: {err or out}")
    if not invoked:
        pytest.skip("CLI not available")
    if errors:
        pytest.fail("; ".join(errors))
    pytest.fail("CLI did not report mismatched vector lengths")

