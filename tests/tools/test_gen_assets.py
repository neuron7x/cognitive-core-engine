# tests/tools/test_gen_assets.py
# Перевірка генерації ресурсів скриптом tools/gen_assets.py
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "gen_assets.py"


@pytest.mark.skipif(not SCRIPT.exists(), reason="tools/gen_assets.py not found")
def test_gen_assets_script_runs_and_produces_files(tmp_path, monkeypatch):
    """
    Тест перевіряє:
      1) скрипт виконується з кодом 0;
      2) створюються очікувані артефакти;
      3) ідемпотентність — повторний запуск також повертає 0.
    """

    # 1) Перший запуск у тимчасовому каталозі
    proc1 = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=str(tmp_path),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    assert proc1.returncode == 0, (
        f"gen_assets.py failed:\nSTDOUT:\n{proc1.stdout}\nSTDERR:\n{proc1.stderr}"
    )

    expected_assets = [
        tmp_path / "assets" / "logo.svg",
        tmp_path / "assets" / "og-banner.png",
        tmp_path / "media" / "api-demo.gif",
        tmp_path / "media" / "cli-demo.gif",
    ]

    # 2) Перевірка наявності артефактів і ненульового розміру
    missing = [str(p) for p in expected_assets if not p.exists()]
    assert not missing, f"Missing generated assets: {missing}"

    small = [str(p) for p in expected_assets if p.exists() and p.stat().st_size == 0]
    assert not small, f"Zero-sized assets: {small}"

    # 3) Повторний запуск (ідемпотентність)
    proc2 = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=str(tmp_path),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    assert proc2.returncode == 0, (
        f"Second run failed:\nSTDOUT:\n{proc2.stdout}\nSTDERR:\n{proc2.stderr}"
    )

