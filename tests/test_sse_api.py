import json
import time

import pytest


def test_sse(api_client):
    steps = []
    timestamps = []

    with api_client.stream("GET", "/api/events/sse") as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

        try:
            for line in response.iter_lines():
                if not line:
                    continue
                if isinstance(line, bytes):
                    line = line.decode()
                if line.startswith("data:"):
                    payload = json.loads(line.split(":", 1)[1].strip())
                    steps.append(payload["step"])
                    timestamps.append(time.monotonic())
                    if len(steps) == 5:
                        break
        except Exception as exc:  # pragma: no cover - defensive error reporting
            pytest.fail(f"Error while iterating over SSE stream: {exc}")

    assert steps == [1, 2, 3, 4, 5]

    intervals = [b - a for a, b in zip(timestamps, timestamps[1:])]
    for interval in intervals:
        assert interval >= 0
