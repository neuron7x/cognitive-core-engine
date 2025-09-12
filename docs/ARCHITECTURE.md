# Architecture (Clean Architecture)

Layers:
- domain: entities/invariants
- app: use-cases/services (pure logic)
- api: FastAPI routers (health, math, sse)
- plugins: registry + example
- tests: unit + e2e
