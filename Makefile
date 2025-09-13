.PHONY: setup lint test api docs build cov docker dev

setup:
	python -m venv .venv && . .venv/bin/activate && pip install -U pip && pip install -e .[dev] && pre-commit install

lint:
	ruff check . && ruff format --check . && isort --check-only . && black --check .

test:
	pytest

api:
        uvicorn cognitive_core.api:app --host 0.0.0.0 --port 8000 --reload

docs:
	mkdocs build --strict || true

build:
	python -m build || true

cov:
	pytest --cov=src/cognitive_core --cov-report=xml

docker:
	docker build -t cognitive-core:local .

dev:
	docker compose up -d --build
