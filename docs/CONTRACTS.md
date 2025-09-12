# HTTP API Contract (stable)

- `GET /api/health` → 200, body: `{"status":"ok"}`
- `POST /api/dot`  → 200, body: `{"result": <float>}`
  Request JSON: `{"a":[number,...], "b":[number,...]}`
- `POST /api/solve2x2` → 200, body: `{"x": <float>, "y": <float>}`
  Request JSON: `{"a11":..., "a12":..., "a21":..., "a22":..., "b1":..., "b2":...}`
- `GET /api/events/sse` → 200 (text/event-stream), events: `tick`
