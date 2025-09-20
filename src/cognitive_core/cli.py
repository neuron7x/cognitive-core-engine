"""Command line interface for cognitive_core."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

from . import __version__
from .app.services import dot as dot_service
from .core.math_utils import solve_2x2
from .core.pipeline_executor import PipelineExecutor
from .pipelines import registry as pipeline_registry


class PipelineError(Exception):
    """Base error for pipeline command failures."""


class PipelineNotFoundError(PipelineError):
    """Raised when a pipeline cannot be located."""


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


def _format_pipeline_result(
    *, pipeline_id: str, run_id: str, status: str, artifacts: Iterable[str]
) -> dict[str, Any]:
    """Return a normalized pipeline run payload."""

    return {
        "pipeline_id": pipeline_id,
        "run_id": run_id,
        "status": status,
        "artifacts": list(artifacts),
    }


def _normalize_pipeline_result(data: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize a pipeline run result payload."""

    try:
        pipeline_id = data["pipeline_id"]
        run_id = data["run_id"]
        status = data["status"]
    except KeyError as exc:
        missing = exc.args[0]
        raise PipelineError(f"Pipeline response missing required field '{missing}'") from exc

    artifacts = data.get("artifacts", [])
    if not isinstance(artifacts, list):
        artifacts = list(artifacts)

    return _format_pipeline_result(
        pipeline_id=pipeline_id,
        run_id=run_id,
        status=status,
        artifacts=artifacts,
    )


def _run_pipeline_locally(name: str) -> dict[str, Any]:
    pipeline = pipeline_registry.get_pipeline(name)
    if not pipeline:
        raise PipelineNotFoundError(f"Pipeline '{name}' not found")

    executor = PipelineExecutor()
    try:
        run = executor.execute(pipeline)
    except Exception as exc:  # pragma: no cover - defensive guardrail
        raise PipelineError(f"Pipeline '{name}' execution failed: {exc}") from exc

    return _format_pipeline_result(
        pipeline_id=pipeline.id,
        run_id=run.id,
        status=run.status,
        artifacts=(artifact.name for artifact in run.artifacts),
    )


def _run_pipeline_remotely(name: str, api_url: str) -> dict[str, Any]:
    import httpx

    endpoint = f"{api_url.rstrip('/')}/api/v1/pipelines/run"
    api_key = os.environ.get("COGCTL_API_KEY") or os.environ.get("COG_API_KEY")
    headers = {"X-API-Key": api_key} if api_key else None
    try:
        response = httpx.post(
            endpoint,
            json={"pipeline_id": name},
            timeout=10.0,
            headers=headers,
        )
    except httpx.HTTPError as exc:
        raise PipelineError(f"Failed to contact pipeline API at {endpoint}: {exc}") from exc

    if response.status_code == 404:
        raise PipelineNotFoundError(f"Pipeline '{name}' not found")

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        detail = response.text
        raise PipelineError(
            f"Pipeline '{name}' run request failed with status {response.status_code}: {detail}"
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise PipelineError("Pipeline API returned invalid JSON response") from exc

    return _normalize_pipeline_result(data)


def _run_pipeline(name: str, api_url: str | None) -> dict[str, Any]:
    if api_url:
        return _run_pipeline_remotely(name, api_url)
    return _run_pipeline_locally(name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cogctl")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
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
    p_run.add_argument(
        "--api-url",
        help="Base URL of a running cognitive-core API service. If omitted, the CLI runs pipelines using local definitions.",
    )

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
        api_url = getattr(args, "api_url", None) or os.environ.get("COGCORE_API_URL")
        try:
            result = _run_pipeline(args.name, api_url)
        except PipelineNotFoundError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        except PipelineError as exc:
            print(str(exc), file=sys.stderr)
            return 1

        print(json.dumps(result))
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

