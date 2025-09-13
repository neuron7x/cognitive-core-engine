import hashlib
from pathlib import Path

import pytest

# Skip the tests entirely if the helper module or Pillow is missing
gen_assets = pytest.importorskip("tools.gen_assets")
Image = pytest.importorskip("PIL.Image")

BANNER_SIZE = (1280, 640)
GIF_SIZE = (1280, 720)


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _gif_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as img:
        return img.size


def test_generate_banner(tmp_path: Path) -> None:
    first = gen_assets.generate_banner(tmp_path)
    assert first.exists()
    with Image.open(first) as img:
        assert img.size == BANNER_SIZE
    first_hash = _sha256(first)

    second = gen_assets.generate_banner(tmp_path / "second")
    with Image.open(second) as img:
        assert img.size == BANNER_SIZE
    assert _sha256(second) == first_hash


def test_generate_gifs(tmp_path: Path) -> None:
    first_paths = gen_assets.generate_gifs(tmp_path)
    assert first_paths
    hashes = []
    for path in first_paths:
        assert path.suffix == ".gif"
        assert _gif_size(path) == GIF_SIZE
        hashes.append(_sha256(path))

    second_dir = tmp_path / "second"
    second_paths = gen_assets.generate_gifs(second_dir)
    assert len(first_paths) == len(second_paths)
    for path, expected_hash in zip(second_paths, hashes):
        assert _gif_size(path) == GIF_SIZE
        assert _sha256(path) == expected_hash
