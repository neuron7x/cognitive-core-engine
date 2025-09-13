"""Tests for the asset generation script."""

import importlib.util
import pathlib
import struct

spec = importlib.util.spec_from_file_location(
    "gen_assets",
    pathlib.Path(__file__).resolve().parents[2] / "tools" / "gen_assets.py",
)
gen_assets = importlib.util.module_from_spec(spec)
assert spec.loader is not None  # for type checkers
spec.loader.exec_module(gen_assets)
generate_banner = gen_assets.generate_banner
generate_gifs = gen_assets.generate_gifs


def test_generate_banner(tmp_path):
    out = tmp_path / "banner.png"
    generate_banner(out)
    assert out.exists()
    with out.open("rb") as f:
        assert f.read(8) == b"\x89PNG\r\n\x1a\n"


def _gif_size(path):
    with open(path, "rb") as f:
        header = f.read(10)
    assert header[:6] == b"GIF89a"
    return struct.unpack("<HH", header[6:10])


def test_generate_gifs(tmp_path):
    generate_gifs(tmp_path)
    api = tmp_path / "api-demo.gif"
    cli = tmp_path / "cli-demo.gif"
    assert api.exists() and cli.exists()
    assert _gif_size(api) == (132, 24)
    assert _gif_size(cli) == (132, 24)

