import json
import shlex
import subprocess

import pytest

from cognitive_core.app import services


def _run_cli(args: str):
    for exe in ("cogctl", "python -m cognitive_core.cli"):
        proc = subprocess.run(shlex.split(f"{exe} {args}"), capture_output=True, text=True)
        if proc.returncode == 0 and proc.stdout.strip():
            return json.loads(proc.stdout)
    pytest.skip("CLI not available")


@pytest.mark.integration
def test_dot_consistency(api_client):
    a = [1.0, 2.0, 3.0]
    b = [4.0, 5.0, 6.0]
    service_res = services.dot(a, b)
    api_res = api_client.post("/api/dot", json={"a": a, "b": b}).json()["result"]
    cli_res = _run_cli("dotv 1,2,3 4,5,6")["dot"]
    assert service_res == pytest.approx(api_res)
    assert service_res == pytest.approx(cli_res)


@pytest.mark.integration
def test_solve2x2_consistency(api_client):
    params = {"a": 1, "b": 1, "c": 2, "d": -1, "e": 4, "f": 0}
    service_x, service_y = services.solve_linear_2x2(
        params["a"], params["b"], params["c"], params["d"], params["e"], params["f"]
    )
    api_js = api_client.post("/api/solve2x2", json=params).json()
    cli_js = _run_cli("solve2x2 1 1 2 -1 4 0")
    assert service_x == pytest.approx(api_js["x"]) == pytest.approx(cli_js["x"])
    assert service_y == pytest.approx(api_js["y"]) == pytest.approx(cli_js["y"])
