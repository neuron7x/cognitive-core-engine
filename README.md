# Cognitive Core Engine

![CI](https://github.com/neuron7x/cognitive-core-engine/actions/workflows/ci.yml/badge.svg)
![CodeQL](https://github.com/neuron7x/cognitive-core-engine/actions/workflows/codeql.yml/badge.svg)

**Version:** v0.1.0 · **Release:** 2025-09-12

- API: FastAPI (`/api/health`, `/api/dot`, `/api/solve2x2`, `/api/events/sse`)
- CLI: `cogctl dotv "1,2,3" "4,5,6"`; `cogctl solve2x2 ...`
- Plugins: `plugins/` registry with example (`math.dot`)
- Docs: MkDocs (`docs/`), Ops guide
- Tests: unit + e2e + coverage
- Containers: Dockerfile, docker-compose
- Dev: pre-commit, Ruff/Black/Isort, DevContainer

## Quick start
```bash
python -m venv .venv && . .venv/bin/activate
pip install -e .[dev]
make lint && make test
make api
```

## Docker
```bash
docker compose up -d --build
```


v9.0: Live OpenAI adapter, Redis LUA limiter, Dockerfile, nginx, systemd examples.


## Ready-to-push checklist
1. Set up repo on GitHub and create `main` branch.
2. Add secrets: `GHCR_PAT`, `OPENAI_API_KEY` (optional), `DATABASE_URL`, `REDIS_URL`, `API_KEY`.
3. Run pre-commit install: `pip install pre-commit && pre-commit install`.
4. Run tests: `pytest` (integration tests will be skipped if services not available).
5. Build and push: `git add . && git commit -m "release: prepare v0.1.0" && git push origin main`.

Commit message template:
```
release: prepare v0.1.0
- live OpenAI adapter (opt-in)
- Redis LUA rate-limiter
- production Dockerfile + nginx + systemd examples
- tests adjusted to skip integrations when services missing
```

