from __future__ import annotations

import importlib
from pathlib import Path


def load_plugins() -> None:
    """Scan the plugins package and import all modules.

    Importing modules causes them to register themselves with the plugin
    registry via the ``register`` function.
    """

    base_dir = Path(__file__).resolve().parent
    package = __name__.rsplit(".", 1)[0]

    for path in base_dir.rglob("*.py"):
        if path.name in {"__init__.py", "plugin_loader.py"}:
            continue
        rel = path.relative_to(base_dir).with_suffix("")
        module_name = ".".join((package, *rel.parts))
        importlib.import_module(module_name)
