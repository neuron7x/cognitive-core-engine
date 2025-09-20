# Contributing

Use Conventional Commits. Run `make lint test` before PR.

## Development setup

Install the full development bundle and set up pre-commit hooks:

```bash
pip install -r requirements-dev.txt
pip install pre-commit
pre-commit install
```

The editable install in `requirements-dev.txt` (`-e .[api,test,dev,docs]`) already
provides the runtime, testing, and documentation dependencies, so no additional
pins are required.

## Pre-commit

Before committing, run the hooks against your changes:

```bash
pre-commit run --files <changed files>
```
