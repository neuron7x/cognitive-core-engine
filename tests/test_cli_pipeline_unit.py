import os
from typing import Any

import httpx

from cognitive_core import cli


class _DummyResponse:
    status_code = 200
    text = ""

    def __init__(self, payload: dict[str, Any]):
        self._payload = payload

    def raise_for_status(self) -> None:  # pragma: no cover - behaviour verified via payload
        return None

    def json(self) -> dict[str, Any]:
        return self._payload


def test_run_pipeline_locally_returns_pipeline_identifier():
    result = cli._run_pipeline_locally("sample")
    assert result["pipeline_id"] == "sample"
    assert result["status"]
    assert isinstance(result["artifacts"], list)


def test_run_pipeline_remotely_injects_api_key_header(monkeypatch):
    called = {}

    def fake_post(url: str, *, json: dict[str, Any], timeout: float, headers: dict[str, str] | None):
        called.update({
            "url": url,
            "json": json,
            "timeout": timeout,
            "headers": headers,
        })
        payload = {
            "pipeline_id": json["pipeline_id"],
            "run_id": "remote-123",
            "status": "completed",
            "artifacts": ["result"],
        }
        return _DummyResponse(payload)

    monkeypatch.setenv("COGCTL_API_KEY", "secret-key")
    monkeypatch.delenv("COG_API_KEY", raising=False)
    monkeypatch.setattr(httpx, "post", fake_post)

    result = cli._run_pipeline_remotely("sample", "https://example.test")

    assert called["url"] == "https://example.test/api/v1/pipelines/run"
    assert called["json"] == {"pipeline_id": "sample"}
    assert called["headers"] == {"X-API-Key": "secret-key"}
    assert result["pipeline_id"] == "sample"
    assert result["run_id"] == "remote-123"
    assert result["artifacts"] == ["result"]

    monkeypatch.delenv("COGCTL_API_KEY", raising=False)
    os.environ.pop("COG_API_KEY", None)
