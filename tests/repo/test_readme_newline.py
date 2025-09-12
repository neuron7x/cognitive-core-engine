from pathlib import Path


def test_readme_has_trailing_newline():
    p = Path("README.md")
    assert p.exists()
    txt = p.read_bytes()
    assert len(txt) == 0 or txt.endswith(b"\n")
