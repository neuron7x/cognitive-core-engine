# STABILITY

**Contract:** This v0.1.0 restart preserves public interfaces introduced in v0.1.0.  
- **API** endpoints unchanged: `/api/health`, `/api/dot`, `/api/solve2x2`, `/api/events/sse`.
- **CLI** unchanged: `cogctl` (`dotv`, `solve2x2`).
- **Package** and import paths unchanged: `cognitive_core.*`.
- **Semantic versioning:** MINOR bump → backward compatible; patch may tighten validations only.
- **Dep policy:** no stricter pinned versions; safety checks via CI remain.

Verification: see `tests/compat/test_api_contract.py`.
