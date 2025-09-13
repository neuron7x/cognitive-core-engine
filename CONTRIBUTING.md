# Contributing

Use Conventional Commits. Run `make lint test` before PR.

## Development setup

Install FastAPI with its test dependencies and set up pre-commit hooks:

```bash
pip install 'fastapi[test]'
pip install pre-commit
pre-commit install
```

## Pre-commit

Before committing, run the hooks against your changes:

```bash
pre-commit run --files <changed files>
```
