"""Utilities for generating simple deterministic assets for tests.

This module intentionally keeps the artwork straightforward.  The functions
produce images with fixed dimensions and deterministic pixel data so that the
resulting hashes are stable across runs and machines.  The helpers are used by
the test-suite to verify that asset generation behaves as expected.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw

BANNER_SIZE = (1280, 640)
GIF_SIZE = (1280, 720)


def generate_banner(output_dir: Path | str) -> Path:
    """Generate and return the banner image.

    The banner is a PNG with a soft gradient inspired by the colours used in
    other marketing assets.  The generated image is deterministic so the test
    suite can rely on its checksum.
    """

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    banner_path = directory / "banner.png"

    image = _banner_image()
    image.save(banner_path, format="PNG", optimize=True)
    return banner_path


def generate_gifs(output_dir: Path | str) -> list[Path]:
    """Generate a small collection of looping GIFs.

    Each GIF contains a handful of frames with simple geometric shapes.  The
    palette and animation data are fixed so running the generator in different
    directories yields byte-identical files.
    """

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    definitions: list[tuple[str, Iterable[tuple[int, int, int]]]] = [
        ("pulse", _pulse_palette()),
        ("orbit", _orbit_palette()),
        ("wave", _wave_palette()),
    ]

    paths: list[Path] = []
    for name, palette in definitions:
        gif_path = directory / f"{name}.gif"
        frames = list(_gif_frames(palette))
        first, *rest = frames
        first.save(
            gif_path,
            format="GIF",
            save_all=True,
            append_images=rest,
            duration=160,
            loop=0,
            disposal=2,
        )
        paths.append(gif_path)

    return paths


def _banner_image() -> Image.Image:
    background = Image.new("RGB", BANNER_SIZE, (11, 17, 38))
    overlay = Image.new("RGB", BANNER_SIZE, (0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    width, height = BANNER_SIZE
    gradient_steps = 12
    for index in range(gradient_steps):
        colour = (20 + index * 8, 60 + index * 6, 120 + index * 7)
        draw.rectangle(
            (0, int(height * index / gradient_steps), width, int(height * (index + 1) / gradient_steps)),
            fill=colour,
        )

    blended = Image.blend(background, overlay, alpha=0.55)

    accent = ImageDraw.Draw(blended)
    stripe_width = width // 16
    for stripe in range(0, width, stripe_width * 2):
        accent.rectangle((stripe, 0, stripe + stripe_width, height), outline=None, fill=(35, 88, 196))

    return blended


def _gif_frames(palette: Iterable[tuple[int, int, int]]) -> Iterable[Image.Image]:
    colours = list(palette)
    frame_count = len(colours)
    width, height = GIF_SIZE
    for index, colour in enumerate(colours):
        frame = Image.new("RGB", GIF_SIZE, colour)
        draw = ImageDraw.Draw(frame)

        radius = min(width, height) // 6
        offset = (index * radius) // 2

        draw.ellipse(
            (width // 2 - radius + offset, height // 2 - radius, width // 2 + radius + offset, height // 2 + radius),
            fill=colours[index - 1],
        )
        draw.rectangle(
            (offset, height // 3, offset + width // 3, height // 3 + radius),
            fill=colours[(index + 1) % frame_count],
        )

        yield frame.quantize(colors=64)


def _pulse_palette() -> list[tuple[int, int, int]]:
    return [
        (15, 40, 90),
        (40, 90, 170),
        (90, 150, 220),
        (40, 90, 170),
    ]


def _orbit_palette() -> list[tuple[int, int, int]]:
    return [
        (10, 26, 60),
        (36, 70, 130),
        (70, 120, 190),
        (120, 170, 230),
    ]


def _wave_palette() -> list[tuple[int, int, int]]:
    return [
        (8, 20, 48),
        (28, 60, 120),
        (60, 110, 180),
        (28, 60, 120),
        (8, 20, 48),
    ]

