# Протокол тестування для `cognitive-core-engine`

## Мета
Забезпечити максимально надійний, відтворюваний і повний контроль якості для PR/merge, випусків та щоденного девелопменту.

## Вектори тестування
1. **Unit** — ізоляційні тести модулів `cognitive_core/*`.
2. **API** — FastAPI endpoints: `/api/health`, `/api/dot`, `/api/solve2x2`, `/api/events/sse`.
3. **CLI** — команди `cogctl dotv`, `cogctl solve2x2`.
4. **Plugins** — завантаження та контракт плагінів (приклад: `plugins/math.dot`).
5. **DB/Migrations** — `alembic` (створення тимчасової БД, `upgrade -> downgrade -> upgrade`).
6. **Docs** — збірка `mkdocs` (перевірка навігації/лінків).
7. **Typing** — `mypy` на публічних API/entrypoints.
8. **Static** — `ruff`, `black --check`, `isort --check`.
9. **Security** — `bandit` (SAST), `pip-audit` (supply chain).
10. **Property-based** — `hypothesis` для чисельних функцій (стабільність/інваріанти).
11. **Headers** — безпека відповіді (content-type, cache, CORS/без зайвого).
12. **SSE** — стрімінг подій (`text/event-stream`).

## Gate на PR (обовʼязково зелені)
- Lint, Typecheck, Unit+API tests (coverage ≥ 85% — міряємо, але не блокуємо перший час).
- Security (Bandit, pip-audit). 
- Semantic PR title (Conventional Commits).
- Docs build (не блокуючий перший час, `continue-on-error: true`).

## Як запускати локально
```bash
python -m venv .venv && . .venv/bin/activate
pip install -e .
pip install pytest pytest-cov httpx hypothesis ruff black isort mypy bandit pip-audit mkdocs mkdocs-material alembic sqlalchemy
pytest -q
```

## Звітність
- Артефакти GitHub Actions: `coverage.xml`, HTML coverage, `pytest-report.html`, `security-findings.json`.
- Автоматичний коментар у PR із сумарними метриками (опціонально — codecov).

## Політика і стабільність
- Нові ендпоїнти/CLI — супроводжувати тестами та typing.
- Flaky-тести — маркуємо `@pytest.mark.flaky` і фіксимо протягом 24–48 год.
- Міграції — жоден PR не мержиться, якщо міграції не проходять на чистій БД.
