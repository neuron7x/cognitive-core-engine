# <img src="assets/logo.svg" alt="Логотип" width="48" align="left"/> cognitive-core-engine

> Базовий рушій для когнітивних сервісів із API, CLI та підтримкою плагінів.

[![CI](https://img.shields.io/github/actions/workflow/status/neuron7x/cognitive-core-engine/ci.yml?style=flat-square&logo=github)](https://github.com/neuron7x/cognitive-core-engine/actions/workflows/ci.yml)
[![CodeQL](https://img.shields.io/github/actions/workflow/status/neuron7x/cognitive-core-engine/codeql.yml?style=flat-square&logo=github)](https://github.com/neuron7x/cognitive-core-engine/actions/workflows/codeql.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

## Зміст
- [Огляд](#огляд)
- [Особливості](#особливості)
- [Встановлення](#встановлення)
- [Швидкий старт](#швидкий-старт)
- [API](#api)
- [Security & Configuration](#security--configuration)
  - [Troubleshooting](#troubleshooting)
- [CLI](#cli)
- [Observability / Спостережуваність](#observability--спостережуваність)
- [Тестування](#тестування)
- [Architecture Overview / Огляд архітектури](#architecture-overview--огляд-архітектури)
- [Дорожня карта](#дорожня-карта)
- [Документація](#документація)
- [Спільнота](#спільнота)
- [Ліцензія](#ліцензія)

## Огляд
`cognitive-core-engine` забезпечує базові компоненти для побудови та виконання когнітивних сервісів.  
Проєкт включає API, CLI та інструменти для розробки.

## Особливості
- Відкритий HTTP API на FastAPI
- CLI `cogctl`
- Плагінна система
- Тести та CI
- Структуровані JSON-логи з метриками Prometheus та трасуванням OpenTelemetry

## Встановлення
```bash
pip install -e '.[api,test,dev]'
```

## Швидкий старт

```bash
cogctl --help
pytest
```

### Генерація ресурсів

```bash
python tools/gen_assets.py
```

Скрипт [tools/gen_assets.py](tools/gen_assets.py) створює допоміжні графічні файли у каталогах `assets` та `media`, зокрема:

- `assets/logo.svg`
- `assets/og-banner.png`
- `media/api-demo.gif`
- `media/cli-demo.gif`

## API
Докладніше див. [docs/api.md](docs/api.md).

```bash
# Перевірка стану сервісу
curl -s http://localhost:8000/api/health
# -> {"status": "ok"}

# Обчислення скалярного добутку
curl -s -X POST http://localhost:8000/api/dot \
  -H "Content-Type: application/json" \
  -d '{"a": [1, 2, 3], "b": [4, 5, 6]}'
# -> {"result": 32.0}
```

## Security & Configuration

Скопіюйте приклад конфігурації та налаштуйте ключі:

```bash
cp .env.example .env
```

У `.env` **обов'язково** встановіть ненульове значення `COG_API_KEY` та інші
змінні середовища (`COG_APP_NAME`, `COG_API_PREFIX`, `COG_RATE_LIMIT_RPS`,
`COG_RATE_LIMIT_BURST`). Сервіс повертає помилку `500`, доки ключ не
налаштовано, тому безпечно використовувати репозиторій без попередньо
визначеного секрету.

Журнальний рівень регулюється змінною `COG_LOG_LEVEL` (`INFO` за промовчанням).
Структуровані логи включають `request_id`, `http_method`, `http_route`,
`http_status`, `duration_ms`, а також `trace_id`/`span_id`, якщо активовано
OpenTelemetry трейсер.

Приклад запиту з заголовком `X-API-Key`:

```bash
curl -H "X-API-Key: your_api_key" http://localhost:8000/api/health
```

Параметри обмеження швидкості контролюються змінними `COG_RATE_LIMIT_RPS`
та `COG_RATE_LIMIT_BURST`.

### Troubleshooting

- **Відсутні залежності.** Деякі функції потребують додаткових пакетів
  (`redis`, `requests` тощо). Встановіть їх через `pip install -e '.[api,test,dev]'`.
- **Файл `.env` не знайдено.** Переконайтеся, що скопіювали `.env.example`
  у `.env` або експортували змінні вручну.

## CLI

Ознайомтеся з [docs/operations.md](docs/operations.md) для деталей.

```bash
# Скалярний добуток векторів
cogctl dotv 1,2,3 4,5,6
# -> {"dot": 32.0}

# Розв'язання системи 2x2
cogctl solve2x2 1 2 3 4 5 6
# -> {"x": -4.0, "y": 4.5}
```

## Observability / Спостережуваність

- Прометеєві метрики доступні на [`/metrics`](http://localhost:8000/metrics).
- Middleware `ObservabilityMiddleware` забезпечує структуровані JSON-логи з
  полями `request_id`, `http_status`, `duration_ms`, `client_ip` та
  `trace_id`/`span_id` (коли активовано OpenTelemetry).
- Встановіть `OTEL_EXPORTER_OTLP_ENDPOINT`, щоб надсилати трейси до OTLP
  колектора (Jaeger, Tempo, New Relic тощо).

Приклад запису логів:

```json
{"timestamp": "2025-09-12T10:15:33.102000+00:00", "level": "INFO", "logger": "cognitive_core.utils.telemetry", "message": "request.completed", "module": "telemetry", "function": "dispatch", "line": 198, "request_id": "9f6d4b1e8e7c4a7d9df2f1a4b9d7c1ad", "http_method": "GET", "http_route": "/api/health", "http_status": "200", "duration_ms": 4.12}
```

## Тестування

```bash
pytest

# запуск лише CLI та API тестів
pytest tests/cli/test_cli.py tests/api/test_root.py
```

## Architecture Overview / Огляд архітектури

**EN:** High-level view of the engine. See [docs/architecture.md](docs/architecture.md) for detailed data flow diagrams of the API, pipelines, and plugin system.

**UA:** Високорівневий огляд рушія. Докладні діаграми потоків даних API, пайплайнів та плагінів дивіться у [docs/architecture.md](docs/architecture.md).

- Domain core / Доменне ядро
- Application services / Сервіси застосунку
- FastAPI layer / Шар FastAPI
- Pipeline orchestrator / Оркестратор пайплайнів
- Plugin registry / Реєстр плагінів

## Дорожня карта

* [ ] Опублікувати першу версію на PyPI
* [ ] Розширити каталог плагінів
* [ ] Додати приклади використання

## Документація

- [API](docs/api.md)
- [Архітектура](docs/architecture.md)
- [Операції](docs/operations.md)

## Спільнота

* [Посібник для контриб'юторів](CONTRIBUTING.md)
* [Кодекс поведінки](CODE_OF_CONDUCT.md)
* [Політика безпеки](SECURITY.md)

## Ліцензія

Цей проєкт розповсюджується за ліцензією [MIT](LICENSE).

