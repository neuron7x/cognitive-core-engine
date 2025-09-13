# Contributing

Use Conventional Commits. Run `make lint test` before PR.

## Pre-commit

Install and configure the pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

Before committing, run the hooks against your changes:

```bash
pre-commit run --files <changed files>
```
