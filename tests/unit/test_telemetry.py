from __future__ import annotations

from types import SimpleNamespace

import pytest

from cognitive_core.utils import telemetry


@pytest.fixture
def patched_trace(monkeypatch):
    providers: list[object] = []

    dummy_trace = SimpleNamespace(set_tracer_provider=providers.append)
    monkeypatch.setattr(telemetry, "trace", dummy_trace)
    monkeypatch.setattr(telemetry, "SERVICE_NAME", "service.name", raising=False)

    class DummyResource:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    monkeypatch.setattr(telemetry, "Resource", DummyResource, raising=False)
    return providers


def test_setup_telemetry_skips_console_export_by_default(monkeypatch, patched_trace):
    console_called = False
    processors_created: list[object] = []

    class DummyTracerProvider:
        def __init__(self, *args, **kwargs):
            self.processors: list[object] = []

        def add_span_processor(self, processor):
            self.processors.append(processor)

    def dummy_batch_span_processor(exporter):
        processors_created.append(exporter)
        return SimpleNamespace(exporter=exporter)

    def dummy_console_exporter():
        nonlocal console_called
        console_called = True
        return object()

    monkeypatch.setattr(telemetry, "TracerProvider", DummyTracerProvider, raising=False)
    monkeypatch.setattr(telemetry, "BatchSpanProcessor", dummy_batch_span_processor, raising=False)
    monkeypatch.setattr(telemetry, "ConsoleSpanExporter", dummy_console_exporter, raising=False)

    telemetry.setup_telemetry("test-service")

    assert patched_trace and isinstance(patched_trace[0], DummyTracerProvider)
    assert not console_called
    assert not processors_created
    assert not patched_trace[0].processors


def test_setup_telemetry_enables_console_export_when_requested(monkeypatch, patched_trace):
    processors_created: list[object] = []

    class DummyTracerProvider:
        def __init__(self, *args, **kwargs):
            self.processors: list[object] = []

        def add_span_processor(self, processor):
            self.processors.append(processor)

    class DummyExporter:
        pass

    def dummy_batch_span_processor(exporter):
        processors_created.append(exporter)
        return SimpleNamespace(exporter=exporter)

    monkeypatch.setattr(telemetry, "TracerProvider", DummyTracerProvider, raising=False)
    monkeypatch.setattr(telemetry, "BatchSpanProcessor", dummy_batch_span_processor, raising=False)
    monkeypatch.setattr(telemetry, "ConsoleSpanExporter", DummyExporter, raising=False)

    telemetry.setup_telemetry("test-service", enable_console_export=True)

    assert patched_trace and isinstance(patched_trace[0], DummyTracerProvider)
    assert len(processors_created) == 1
    assert isinstance(processors_created[0], DummyExporter)
    assert (
        patched_trace[0].processors
        and patched_trace[0].processors[0].exporter is processors_created[0]
    )
