import sys, subprocess as sp; cmds=['ruff check .','black --check .','isort --check-only .','pytest -q']; sys.exit(sum(sp.call(c,shell=True) for c in cmds))
