## [Unreleased]
- Added structured JSON logging with OpenTelemetry correlation and configurable
  `COG_LOG_LEVEL`.
- Introduced unified observability middleware exposing Prometheus request metrics
  and request-scoped logging context.
- Documented deployment, upgrade, and incident response runbooks in
  `docs/operations.md` and expanded README observability guidance.

## v0.1.0 — 2025-09-12
- Unified version to v0.1.0 across code and docs.
- Moved runtime deps into `pyproject.toml`; thinned `requirements.txt` to `-e .[dev]`.
- Fixed Alembic target metadata and ensured `cognitive_core/db.py` with `Base` exists.
- Replaced LICENSE with full MIT text.
- Adjusted Dockerfile to install the package and added a HEALTHCHECK.
- Synced README/STABILITY/OPERATIONS version mentions.

# Changelog

## [v5.0] - 2025-09-12
- Rename & normalize: repository **cognitive-core-engine**, package **cognitive_core**, CLI **cogctl**.
- Keep production GitHub layout, CI, Docker, DevContainer, tests, docs.

## [v5.1] - 2025-09-12
- Stability-preserving restart: kept API/CLI/package contracts intact.
- Added `STABILITY.md`, API contract doc, and compat test suite.
