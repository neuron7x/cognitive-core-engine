import json
import time


def test_sse(api_client):
    steps = []
    timestamps = []

    with api_client.stream("GET", "/api/events/sse") as response:
        assert "text/event-stream" in response.headers.get("content-type", "")

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

    assert steps == [1, 2, 3, 4, 5]

    intervals = [b - a for a, b in zip(timestamps, timestamps[1:])]
    for interval in intervals:
        assert interval >= 0
