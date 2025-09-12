from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ....github.scripts.zipci_lib import check_zip_safety  # type: ignore
from .util import to_json


@dataclass
class Args:
    zip: str
    max_files: int = 20000
    max_total: int = 250 * 1024 * 1024
    max_per_file: int = 50 * 1024 * 1024
    max_ratio: float = 120.0


def run_scan(ns: Any) -> bool:
    reasons = check_zip_safety(ns.zip, ns.max_files, ns.max_total, ns.max_per_file, ns.max_ratio)
    ok = len(reasons) == 0
    print(to_json(dict(zip=ns.zip, ok=ok, reasons=reasons)))
    return 0 if ok else 1
