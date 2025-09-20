# API

> **Security requirement:** перед тим як викликати ендпоінти, встановіть середовищну змінну `COG_API_KEY` і передавайте її значення у кожному запиті через заголовок `X-API-Key`. Якщо ключ не налаштовано або він порожній, сервер відповідає помилкою `500`. Якщо заголовок відсутній або містить некоректне значення, сервер повертає `403 Forbidden`.

## GET /api/health
Request:
```http
GET /api/health HTTP/1.1
X-API-Key: <your-api-key>
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
X-API-Key: <your-api-key>

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
X-API-Key: <your-api-key>

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
Request:
```http
GET /api/events/sse HTTP/1.1
Accept: text/event-stream
X-API-Key: <your-api-key>
```
Response:
```text
data: hello

data: world
```
