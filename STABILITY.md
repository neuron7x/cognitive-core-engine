# STABILITY

**Contract:** This v0.1.1 release preserves and extends the public interfaces introduced in v0.1.0.
- **API** endpoints remain stable: `/api/health`, `/api/dot`, `/api/solve2x2`, `/api/events/sse`, plus the pipeline routes `GET /api/v1/pipelines/{pipeline_id}`, `POST /api/v1/pipelines/run`, and `POST /api/pipelines/aots_debate`.
- **CLI** remains stable: `cogctl` keeps `dotv` and `solve2x2` and now also supports `ping`, `migrate {status,up,down}`, `pipeline run --name [--api-url]`, and `plugin {list,install,remove}`.
- **Package** and import paths unchanged: `cognitive_core.*`.
- **Semantic versioning:** MINOR bump → backward compatible; the added endpoints and subcommands are optional extensions that preserve existing behavior, while patch releases may tighten validations only.
- **Dep policy:** no stricter pinned versions; safety checks via CI remain.

Verification: see `tests/compat/test_api_contract.py`, `tests/test_pipelines_api.py`, and `tests/cli/test_cli.py`.
