PY=python
VENV=.venv

.PHONY: setup fmt lint type test all

setup:
	$(PY) -m venv $(VENV)
	. $(VENV)/bin/activate && pip install -U pip && pip install -e .[dev]

fmt:
	black .

lint:
	ruff check .
	codespell || true

type:
	mypy tools

test:
	pytest

all: lint type test
