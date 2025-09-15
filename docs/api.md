# API

> **Security requirement:** перед тим як викликати ендпоінти, встановіть
> середовищну змінну `COG_API_KEY`. Якщо ключ не налаштовано або він порожній,
> сервер відповідає помилкою `500` й відхиляє запити.

## GET /api/health
Request:
```http
GET /api/health HTTP/1.1
```
Response:
```json
{
  "status": "ok"
}
```

## POST /api/dot
Request:
```http
POST /api/dot HTTP/1.1
Content-Type: application/json

{
  "a": [1, 2, 3],
  "b": [4, 5, 6]
}
```
Response:
```json
{
  "result": 32.0
}
```

## POST /api/solve2x2
Request:
```http
POST /api/solve2x2 HTTP/1.1
Content-Type: application/json

{
  "a": 1,
  "b": 1,
  "c": 1,
  "d": -1,
  "e": 1,
  "f": 0
}
```
Response:
```json
{
  "x": 0.5,
  "y": 0.5
}
```

## GET /api/events/sse
Server-Sent Events stream providing real-time messages.
Response:
```text
data: hello

data: world
```
