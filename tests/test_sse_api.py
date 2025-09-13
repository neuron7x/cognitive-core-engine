import json
import time


def test_sse(api_client):
    r = api_client.get("/api/events/sse", stream=True)
    assert "text/event-stream" in r.headers.get("content-type", "")

    steps = []
    timestamps = []

    for line in r.iter_lines():
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
        assert 0.15 <= interval <= 0.3
