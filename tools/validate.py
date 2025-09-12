import subprocess as sp
import sys

cmds = ["ruff check .", "black --check .", "isort --check-only .", "pytest -q"]
sys.exit(sum(sp.call(c, shell=True) for c in cmds))
