import argparse
import json
import sys

from .core.math_utils import dot, solve_2x2


def main(argv=None):
    parser = argparse.ArgumentParser(prog="cogctl")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_dot = sub.add_parser("dotv")
    p_dot.add_argument("a")
    p_dot.add_argument("b")
    p_solve = sub.add_parser("solve2x2")
    for k in ("a", "b", "c", "d", "e", "f"):
        p_solve.add_argument(k, type=float)
    args = parser.parse_args(argv)
    if args.cmd == "dotv":
        a = [float(x) for x in args.a.split(",") if x]
        b = [float(x) for x in args.b.split(",") if x]
        n = min(len(a), len(b))
        print(json.dumps({"dot": dot(a[:n], b[:n])}))
        return 0
    if args.cmd == "solve2x2":
        x, y = solve_2x2(args.a, args.b, args.c, args.d, args.e, args.f)
        print(json.dumps({"x": x, "y": y}))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
