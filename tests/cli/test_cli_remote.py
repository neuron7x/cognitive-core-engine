import pytest

from cognitive_core import cli


class _DummyResponse:
    status_code = 200

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return {
            "pipeline_id": "sample",
            "run_id": "remote-run",
            "status": "queued",
            "artifacts": [],
        }


def test_run_pipeline_remotely_requires_api_key(monkeypatch):
    monkeypatch.delenv("COGCTL_API_KEY", raising=False)
    monkeypatch.delenv("COG_API_KEY", raising=False)

    with pytest.raises(cli.PipelineError):
        cli._run_pipeline_remotely("sample", "http://example.com")


def test_run_pipeline_remotely_sends_api_key_header(monkeypatch):
    monkeypatch.setenv("COGCTL_API_KEY", "cli-secret")
    monkeypatch.delenv("COG_API_KEY", raising=False)

    calls: dict = {}

    def fake_post(url, *, json, timeout, headers):
        calls["url"] = url
        calls["json"] = json
        calls["timeout"] = timeout
        calls["headers"] = headers
        return _DummyResponse()

    monkeypatch.setattr("httpx.post", fake_post)

    result = cli._run_pipeline_remotely("sample", "http://api.local")

    assert calls["url"].endswith("/api/v1/pipelines/run")
    assert calls["json"] == {"pipeline_id": "sample"}
    assert calls["timeout"] == 10.0
    assert calls["headers"] == {"X-API-Key": "cli-secret"}
    assert result == {
        "pipeline_id": "sample",
        "run_id": "remote-run",
        "status": "queued",
        "artifacts": [],
    }
