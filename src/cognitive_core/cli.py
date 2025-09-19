"""Command line interface for cognitive_core."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from .app.services import dot as dot_service
from .core.math_utils import solve_2x2


# Demo registry of available pipelines.
_PIPELINE_REGISTRY: dict[str, str] = {
    "demo": "Demo pipeline",
}


def _run_alembic(*args: str) -> int:
    """Run an alembic command if alembic is installed.

    Parameters
    ----------
    *args:
        Arguments passed directly to the ``alembic`` command line tool.

    Returns
    -------
    int
        Exit code from the command (``0`` on success).
    """

    cfg = Path(__file__).resolve().parent.parent.parent / "alembic.ini"
    env = os.environ.copy()
    env.setdefault("DATABASE_URL", "sqlite://")
    try:
        return subprocess.run(["alembic", "-c", str(cfg), *args], env=env).returncode
    except FileNotFoundError:
        # Alembic isn't installed; treat as a no-op for demo purposes.
        print("alembic not installed", file=sys.stderr)
        return 0


def _install_allowlisted_plugin(module: str) -> None:
    """Install an allowlisted plugin module after integrity verification."""

    from .plugins import REGISTRY
    from .plugins.plugin_loader import (
        PluginVerificationError,
        load_plugin_module,
    )

    spec = load_plugin_module(module)

    if spec.marker is not None and spec.marker not in REGISTRY:
        raise PluginVerificationError(
            f"Plugin '{module}' did not register expected marker '{spec.marker}'."
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cogctl")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # basic math helpers kept for compatibility
    p_dot = sub.add_parser("dotv")
    p_dot.add_argument("a")
    p_dot.add_argument("b")

    p_solve = sub.add_parser("solve2x2")
    for k in ("a", "b", "c", "d", "e", "f"):
        p_solve.add_argument(k, type=float)

    # new commands
    sub.add_parser("ping")

    p_migrate = sub.add_parser("migrate")
    migrate_sub = p_migrate.add_subparsers(dest="action", required=True)
    migrate_sub.add_parser("status")
    migrate_sub.add_parser("up")
    migrate_sub.add_parser("down")

    p_pipeline = sub.add_parser("pipeline")
    pipeline_sub = p_pipeline.add_subparsers(dest="action", required=True)
    p_run = pipeline_sub.add_parser("run")
    p_run.add_argument("--name", required=True)

    p_plugin = sub.add_parser("plugin")
    plugin_sub = p_plugin.add_subparsers(dest="action", required=True)
    plugin_sub.add_parser("list")
    p_install = plugin_sub.add_parser("install")
    p_install.add_argument("module")
    p_remove = plugin_sub.add_parser("remove")
    p_remove.add_argument("name")

    return parser


def handle_args(args: argparse.Namespace) -> int:
    if args.cmd == "dotv":
        a = [float(x) for x in args.a.split(",") if x]
        b = [float(x) for x in args.b.split(",") if x]
        try:
            result = dot_service(a, b)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(json.dumps({"dot": result}))
        return 0

    if args.cmd == "solve2x2":
        x, y = solve_2x2(args.a, args.b, args.c, args.d, args.e, args.f)
        print(json.dumps({"x": x, "y": y}))
        return 0

    if args.cmd == "ping":
        print("pong")
        return 0

    if args.cmd == "migrate":
        if args.action == "status":
            return _run_alembic("current")
        if args.action == "up":
            return _run_alembic("upgrade", "head")
        if args.action == "down":
            return _run_alembic("downgrade", "-1")
        return 1

    if args.cmd == "pipeline" and args.action == "run":
        pipeline_name = args.name
        if pipeline_name not in _PIPELINE_REGISTRY:
            available = ", ".join(sorted(_PIPELINE_REGISTRY)) or "<none>"
            print(
                f"Pipeline '{pipeline_name}' not found. Available pipelines: {available}",
                file=sys.stderr,
            )
            return 1

        print(f"Running pipeline {pipeline_name}")
        return 0

    if args.cmd == "plugin":
        from .plugins import REGISTRY
        from .plugins.plugin_loader import load_plugins

        if args.action == "list":
            load_plugins()
            for meta, _ in REGISTRY.values():
                print(f"{meta.name} {meta.version}")
            return 0

        if args.action == "install":
            from .plugins.plugin_loader import PluginVerificationError

            try:
                _install_allowlisted_plugin(args.module)
                print(f"Installed {args.module}")
                return 0
            except ModuleNotFoundError:
                print(f"Plugin module {args.module} not found", file=sys.stderr)
                return 1
            except PluginVerificationError as exc:
                print(str(exc), file=sys.stderr)
                return 1

        if args.action == "remove":
            if REGISTRY.pop(args.name, None):
                print(f"Removed {args.name}")
                return 0
            print(f"Plugin {args.name} not installed", file=sys.stderr)
            return 1

    return 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return handle_args(args)


if __name__ == "__main__":
    sys.exit(main())

