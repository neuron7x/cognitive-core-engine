import asyncio
import contextlib
import time
from functools import wraps

try:
    from prometheus_client import Counter, Histogram
except Exception:  # pragma: no cover - fallback when library missing

    class _Metric:
        def labels(self, **_kwargs):
            return self

        def observe(self, *_args, **_kwargs):
            return None

        def inc(self, *_args, **_kwargs):
            return None

    def Histogram(*_args, **_kwargs):  # type: ignore[override]
        return _Metric()

    def Counter(*_args, **_kwargs):  # type: ignore[override]
        return _Metric()


try:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
except Exception:  # pragma: no cover - fallback when library missing
    trace = None  # type: ignore


REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency", ["route"])
LLM_TOKENS = Counter("llm_tokens_total", "LLM tokens processed", ["route"])


def setup_telemetry(service_name: str = "cognitive-core-engine") -> None:
    """Initialise tracing providers if OpenTelemetry is available."""
    if trace is None:  # pragma: no cover - graceful degradation
        return
    resource = Resource(attributes={SERVICE_NAME: service_name})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)


def instrument_route(route_name: str):
    """Decorator to time requests and create trace spans."""

    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                tracer = trace.get_tracer(__name__) if trace else None
                span_cm = (
                    tracer.start_as_current_span(route_name) if tracer else contextlib.nullcontext()
                )
                with span_cm:
                    start = time.perf_counter()
                    result = await func(*args, **kwargs)
                    REQUEST_LATENCY.labels(route=route_name).observe(time.perf_counter() - start)
                    return result

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                tracer = trace.get_tracer(__name__) if trace else None
                span_cm = (
                    tracer.start_as_current_span(route_name) if tracer else contextlib.nullcontext()
                )
                with span_cm:
                    start = time.perf_counter()
                    result = func(*args, **kwargs)
                    REQUEST_LATENCY.labels(route=route_name).observe(time.perf_counter() - start)
                    return result

            return sync_wrapper

    return decorator


def record_llm_tokens(route_name: str, tokens: int) -> None:
    """Record the number of tokens processed by an endpoint."""
    LLM_TOKENS.labels(route=route_name).inc(tokens)
