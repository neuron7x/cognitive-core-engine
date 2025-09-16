#!/usr/bin/env python3
"""Validate that requirements.lock is consistent with pyproject.toml."""

from __future__ import annotations

import sys
from pathlib import Path

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - fallback for <3.11
    import tomli as tomllib  # type: ignore[no-redef]

from packaging.requirements import Requirement
from packaging.version import Version


LOCK_FILENAME = "requirements.lock"
PYPROJECT_FILENAME = "pyproject.toml"


def load_lock(path: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    entries: list[str] = []
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "==" not in line:
            raise SystemExit(f"Invalid requirement line in {path}: {raw_line!r}")
        name, version = line.split("==", 1)
        normalized = name.strip().lower().replace("_", "-")
        if normalized in mapping and mapping[normalized] != version.strip():
            raise SystemExit(
                f"Duplicate requirement for {normalized} with conflicting versions in {path}."
            )
        mapping[normalized] = version.strip()
        entries.append(normalized)

    if entries != sorted(entries):
        raise SystemExit(
            "requirements.lock entries must be sorted alphabetically by package name."
        )

    return mapping


def iter_dependency_requirements(pyproject: Path) -> dict[str, list[Requirement]]:
    data = tomllib.loads(pyproject.read_text())
    project = data.get("project", {})
    collected: list[Requirement] = []

    for item in project.get("dependencies", []) or []:
        collected.append(Requirement(item))

    optional = project.get("optional-dependencies", {}) or {}
    for extra_deps in optional.values():
        for item in extra_deps:
            collected.append(Requirement(item))

    # Deduplicate by normalized name while preserving all specifiers for validation
    by_name: dict[str, list[Requirement]] = {}
    for req in collected:
        normalized = req.name.lower().replace("_", "-")
        by_name.setdefault(normalized, []).append(req)

    return by_name


def validate(lock: dict[str, str], grouped_requirements: dict[str, list[Requirement]]) -> int:
    errors: list[str] = []
    for name, requirements in sorted(grouped_requirements.items()):
        if name not in lock:
            errors.append(f"Missing {name} in {LOCK_FILENAME}.")
            continue

        pinned_version = Version(lock[name])
        for req in requirements:
            if req.specifier and pinned_version not in req.specifier:
                errors.append(
                    f"Pinned version {pinned_version} for {name} does not satisfy specifier {req.specifier}."
                )

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    return 0


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    lock_path = repo_root / LOCK_FILENAME
    pyproject_path = repo_root / PYPROJECT_FILENAME

    if not lock_path.exists():
        print(f"ERROR: {LOCK_FILENAME} not found at {lock_path}.")
        return 1
    if not pyproject_path.exists():
        print(f"ERROR: {PYPROJECT_FILENAME} not found at {pyproject_path}.")
        return 1

    lock = load_lock(lock_path)
    grouped = iter_dependency_requirements(pyproject_path)
    return validate(lock, grouped)


if __name__ == "__main__":
    sys.exit(main())
