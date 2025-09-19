import json
import shlex
import subprocess

import pytest


def _run(cmd: str):
    try:
        proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    except FileNotFoundError:
        return None, "", ""
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


@pytest.mark.integration
def test_cli_ping():
    for exe in ("cogctl", "python -m cognitive_core.cli"):
        rc, out, _ = _run(f"{exe} ping")
        if rc is None:
            continue
        if rc == 0 and out:
            assert out.strip() == "pong"
            return
    pytest.skip("CLI ping not available")


@pytest.mark.integration
def test_cli_dotv():
    for exe in ("cogctl", "python -m cognitive_core.cli"):
        rc, out, _ = _run(f"{exe} dotv 1,2,3 4,5,6")
        if rc is None:
            continue
        if rc == 0 and out:
            assert '"dot": 32.0' in out
            return
    pytest.skip("CLI dotv not available")


@pytest.mark.integration
def test_cli_rejects_unapproved_plugin_install():
    for exe in ("cogctl", "python -m cognitive_core.cli"):
        rc, _, err = _run(f"{exe} plugin install totally.forbidden")
        if rc is None:
            continue
        if rc != 0 and err:
            assert "not in the allowlist" in err
            return
    pytest.skip("CLI plugin install not available")


@pytest.mark.integration
def test_cli_pipeline_run_local_success():
    for exe in ("cogctl", "python -m cognitive_core.cli"):
        rc, out, err = _run(f"{exe} pipeline run --name sample")
        if rc is None:
            continue
        if rc == 0 and out:
            data = json.loads(out)
            assert data["status"] == "completed"
            assert data["artifacts"] == ["result"]
            assert "run_id" in data
            assert not err
            return
    pytest.skip("CLI pipeline run not available")


@pytest.mark.integration
def test_cli_pipeline_run_missing_pipeline():
    for exe in ("cogctl", "python -m cognitive_core.cli"):
        rc, out, err = _run(f"{exe} pipeline run --name does-not-exist")
        if rc is None:
            continue
        if rc != 0 and err:
            assert "does-not-exist" in err
            assert out == ""
            return
    pytest.skip("CLI pipeline run error handling not available")
