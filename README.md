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
- [Тестування](#тестування)
- [Architecture Overview / Огляд архітектури](#architecture-overview--огляд-архітектури)
- [Дорожня карта](#дорожня-карта)
- [Документація](#документація)
- [Спільнота](#спільнота)
- [Ліцензія](#ліцензія)

## Огляд
`cognitive-core-engine` забезпечує базові компоненти для побудови та виконання когнітивних сервісів.
Проєкт включає HTTP API на FastAPI, CLI `cogctl`, систему плагінів та готові пайплайни, які можна розширювати у власних сценаріях.

## Особливості
- Відкритий HTTP API на FastAPI  
- CLI `cogctl`  
- Плагінна система  
- Тести та CI  

## Встановлення
```bash
pip install -e '.[api,test,dev]'
```

## Швидкий старт

```bash
cogctl --help
python -m cognitive_core.cli dotv 1,2,3 4,5,6
uvicorn cognitive_core.api.main:app --host 0.0.0.0 --port 8000
```

## Живі приклади

| Сценарій | Команда | Очікуваний результат |
| --- | --- | --- |
| Перевірити роботу CLI | `cogctl status` | JSON зі станом сервісів та версією рушія |
| Обчислити скалярний добуток | `cogctl dotv 1,2,3 4,5,6` | `{ "dot": 32.0 }` |
| Виконати пайплайн у Python | `python - <<'PY'
from cognitive_core.engine import VectorEngine

engine = VectorEngine()
result = engine.dot([1, 2, 3], [4, 5, 6])
print(result)
PY` | `32.0` в стандартному виводі |
| Перевірити API | `curl -s http://localhost:8000/api/health` | `{ "status": "ok" }` |

> **Порада.** У CLI та HTTP API доступні й інші пайплайни (розв'язувач систем, нормалізація векторів тощо). Скористайтесь `cogctl --help` або відкрийте [інтерактивну документацію FastAPI](http://localhost:8000/docs), щоб переглянути повний перелік доступних команд та маршрутів.

### Брендові ресурси

Графічні матеріали зберігаються безпосередньо в репозиторії; окремий генератор наразі не постачається.
Актуальні файли розміщені у каталозі `assets/`, зокрема:

- `assets/logo.svg`

Якщо створюєте нові банери чи демонстраційні матеріали, згенеруйте їх уручну та додайте до відповідних каталогів проєкту.

## Docker

```bash
docker build -t cognitive-core:local .
docker run --rm -p 8000:8000 cognitive-core:local
```

Контейнер збирається з непривілейованим користувачем `appuser` (UID/GID 1000). Під час збірки Dockerfile встановлює права доступу до ключових директорій (`/app/bin`, `/app/tools` та ін.) і позначає службові скрипти як виконувані. Якщо монтуєте локальний каталог у `/app`, переконайтеся, що права доступу сумісні з цим користувачем або відкоригуйте їх заздалегідь.

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

Приклад запиту з заголовком `X-API-Key`:

```bash
curl -H "X-API-Key: your_api_key" http://localhost:8000/api/health
```

Параметри обмеження швидкості контролюються змінними `COG_RATE_LIMIT_RPS`
та `COG_RATE_LIMIT_BURST`.

Якщо сервіс працює за балансувальником (Nginx, Envoy, Kubernetes Ingress тощо),
увімкніть довіру до проксі-заголовків, аби ліміти розраховувалися за справжніми
клієнтськими IP-адресами:

```bash
export COG_TRUST_PROXY_HEADERS=true
export COG_TRUSTED_PROXY_HEADER=X-Forwarded-For  # або власна назва заголовка
```

Сервіс зчитує ліву «публічну» адресу з вказаного заголовка та використовує її
для сегментації rate limit. Якщо жодна адреса не підходить, middleware
повертається до IP підключеного клієнта.

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

## Тестування

```bash
pytest

# запуск лише CLI та API тестів
pytest tests/cli/test_cli.py tests/api/test_root.py

# навантажувальне тестування Locust
export COG_API_KEY=your_api_key
# або передайте --api-key / змінну LOCUST_API_KEY безпосередньо до Locust
uvicorn cognitive_core.api.main:app --host 0.0.0.0 --port 8000 &
LOCUST_PID=$!
locust --headless --users 5 --spawn-rate 5 --run-time 15s \
  --host http://localhost:8000 \
  --locustfile tests/load/locustfile.py
kill $LOCUST_PID
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

* [x] Опублікувати першу версію на PyPI
* [ ] Розширити каталог плагінів
* [x] Додати приклади використання

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

