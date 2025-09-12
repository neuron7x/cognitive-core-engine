# cognitive-core-engine

## Огляд
`cognitive-core-engine` забезпечує базові компоненти для побудови та виконання когнітивних сервісів. Проєкт включає API, CLI та інструменти для розробки.

## Встановлення
```bash
pip install -e '.[api,test,dev]'
```

## Швидкий старт

### API
Запустіть HTTP API для локальної розробки:
```bash
uvicorn cognitive_core.api:app --reload
```

### CLI
Скористайтеся інтерфейсом командного рядка:
```bash
cogctl --help
```

## Тестування
```bash
pytest
```

## Документація
Докладніше у [docs/](docs/).

