import pathlib

import yaml


def test_ci_yaml_parses():
    p = pathlib.Path(".github/workflows/ci.yml")
    assert p.exists()
    with p.open("r", encoding="utf-8") as f:
        y = yaml.safe_load(f)
    assert "jobs" in y and "on" in y
