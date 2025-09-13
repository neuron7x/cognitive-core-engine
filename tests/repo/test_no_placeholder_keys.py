from __future__ import annotations

from pathlib import Path

FORBIDDEN = ["YOUR_API_KEY" + "_HERE", "change" + "me"]


def test_no_placeholder_api_keys():
    root = Path(__file__).resolve().parents[2]
    offenders: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix == ".pyc" or path == Path(__file__):
            continue
        try:
            text = path.read_text(errors="ignore")
        except Exception:
            continue
        for token in FORBIDDEN:
            if token in text:
                offenders.append(f"{token} in {path}")
    assert not offenders, f"placeholder secrets found: {offenders}"
