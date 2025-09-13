
.PHONY: setup lint test coverage security fmt api docs build docker dev bench

setup:
	@if [ -f requirements.txt ] || [ -f pyproject.toml ]; then \
	python -m pip install -U pip; \
	if [ -f pyproject.toml ]; then pip install -e .[dev]; elif [ -f requirements.txt ]; then pip install -r requirements.txt; fi; \
	fi
	@if [ -f package.json ]; then npm install; fi
	@if [ -f go.mod ]; then go mod download; fi
	@if [ -f Cargo.toml ]; then cargo fetch; fi
	@if [ -f pom.xml ]; then mvn -B dependency:resolve || true; fi

lint:
	@if [ -f requirements.txt ] || [ -f pyproject.toml ]; then \
	ruff .; \
	mypy .; \
	bandit -r . || true; \
	fi
	@if [ -f package.json ]; then \
	npx eslint . || true; \
	npx tsc -p . || true; \
	fi
	@if [ -f go.mod ]; then go vet ./...; fi
	@if [ -f Cargo.toml ]; then cargo clippy --all-targets --all-features -- -D warnings || true; fi
	@if [ -f pom.xml ]; then mvn -B -q verify -DskipTests; fi

test:
	@if [ -f requirements.txt ] || [ -f pyproject.toml ]; then pytest; fi
	@if [ -f package.json ]; then npx jest; fi
	@if [ -f go.mod ]; then go test ./...; fi
	@if [ -f Cargo.toml ]; then cargo test; fi
	@if [ -f pom.xml ]; then mvn -B test; fi

bench:
	@if [ -f requirements.txt ] || [ -f pyproject.toml ]; then pytest tests/benchmarks --benchmark-save=bench --benchmark-json=benchmarks.json; fi

coverage:
	@if [ -f requirements.txt ] || [ -f pyproject.toml ]; then pytest --cov=. --cov-report=xml; fi
	@if [ -f package.json ]; then npx jest --coverage; fi
	@if [ -f go.mod ]; then go test ./... -coverprofile=cover.out; fi
	@if [ -f Cargo.toml ]; then cargo tarpaulin --out Xml || true; fi
	@if [ -f pom.xml ]; then mvn -B jacoco:report; fi

security:
	@if [ -f requirements.txt ] || [ -f pyproject.toml ]; then bandit -r . && safety check || true; fi
	@if [ -f package.json ]; then npm audit || true; fi
	@if [ -f go.mod ]; then govulncheck ./... || true; fi
	@if [ -f Cargo.toml ]; then cargo audit || true; fi
	@if [ -f pom.xml ]; then mvn -B org.owasp:dependency-check-maven:check || true; fi

fmt:
	@if [ -f requirements.txt ] || [ -f pyproject.toml ]; then \
	ruff --fix .; \
	black .; \
	fi
	@if [ -f package.json ]; then npx eslint . --fix || true; fi
	@if [ -f go.mod ]; then find . -name '*.go' -print0 | xargs -0 gofmt -w; fi
	@if [ -f Cargo.toml ]; then cargo fmt; fi

api:
	uvicorn cognitive_core.api.main:app --host 0.0.0.0 --port 8000 --reload

docs:
	mkdocs build --strict || true

build:
	python -m build || true

docker:
	docker build -t cognitive-core:local .

dev:
	docker compose up -d --build
