## v0.1.1 — 2025-09-20
- Bundled pipeline packages and their registry in the distribution manifest so published wheels include runnable flows out of the box.
- Added an opt-in console OpenTelemetry exporter with configuration docs and regression coverage for local diagnostics.
- Tightened pipeline tooling by propagating `pipeline_id` in run results and enabling remote runs to pass API keys from the CLI.
- Cached agent role lookups to avoid repeatedly reading pipeline metadata during routing.
- Hardened deployment and security by dropping baked-in API keys from the systemd unit and redacting secrets in rate limiter logs.
- Improved vector memory adapters to reuse prepared statements and trim result parsing overhead.

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
