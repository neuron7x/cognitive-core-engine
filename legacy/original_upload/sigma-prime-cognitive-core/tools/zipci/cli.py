from __future__ import annotations
import argparse, sys
from .runner import run_scan

def main() -> int:
    p = argparse.ArgumentParser("zipci-scan — safe ZIP checker (JSON output)")
    p.add_argument("zip", help="path to zip file")
    p.add_argument("--max-files", type=int, default=20000)
    p.add_argument("--max-total", type=int, default=250*1024*1024)
    p.add_argument("--max-per-file", type=int, default=50*1024*1024)
    p.add_argument("--max-ratio", type=float, default=120.0)
    args = p.parse_args()
    code = run_scan(args)
    return int(code)

if __name__ == "__main__":
    raise SystemExit(main())
