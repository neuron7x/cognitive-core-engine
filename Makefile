.PHONY: setup lint typecheck test cov run docs docker

setup:
	python -m pip install -U pip
	pip install -e '.[api,test,dev,docs,security]'

lint:
	ruff check . && black --check . && isort --check-only .

typecheck:
	mypy . --install-types --non-interactive

test:
	pytest

cov:
	pytest --cov=cognitive_core --cov-report=term-missing

run:
	uvicorn cognitive_core.api:app --host 0.0.0.0 --port 8000

docs:
	mkdocs serve -a 0.0.0.0:8001

docker:
	docker build -t cognitive-core-engine:local .
