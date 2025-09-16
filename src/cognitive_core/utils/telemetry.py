from __future__ import annotations

import asyncio
import contextlib
import importlib.util
import logging
import time
import uuid
from contextvars import Token
from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from .logging import bind_log_context, reset_log_context

_PROMETHEUS_SPEC = importlib.util.find_spec("prometheus_client")
if _PROMETHEUS_SPEC is not None:  # pragma: no branch - optional dependency
    from prometheus_client import Counter, Histogram  # type: ignore
else:  # pragma: no cover - executed when dependency missing

    class _Metric:
        def labels(self, **_kwargs: Any):
            return self

        def observe(self, *_args: Any, **_kwargs: Any) -> None:
            return None

        def inc(self, *_args: Any, **_kwargs: Any) -> None:
            return None

    def Histogram(*_args: Any, **_kwargs: Any):  # type: ignore[override]
        return _Metric()

    def Counter(*_args: Any, **_kwargs: Any):  # type: ignore[override]
        return _Metric()


_TRACE_SPEC = None
if importlib.util.find_spec("opentelemetry") is not None:
    _TRACE_SPEC = importlib.util.find_spec("opentelemetry.trace")

if _TRACE_SPEC is not None:  # pragma: no branch - optional dependency
    from opentelemetry import trace  # type: ignore
    from opentelemetry.trace import Status, StatusCode  # type: ignore
else:  # pragma: no cover - executed when dependency missing
    trace = None  # type: ignore[assignment]
    Status = None  # type: ignore[assignment]
    StatusCode = None  # type: ignore[assignment]


REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency", ["route"])
HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests processed by the API",
    ["method", "route", "status"],
)
HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration distribution",
    ["method", "route", "status"],
)
LLM_TOKENS = Counter("llm_tokens_total", "LLM tokens processed", ["route"])

logger = logging.getLogger(__name__)

_T = TypeVar("_T")


def setup_telemetry(service_name: str = "cognitive-core-engine") -> None:
    """Initialise tracing providers if OpenTelemetry is available."""

    if trace is None:  # pragma: no cover - graceful degradation when OTel missing
        return

    sdk_trace_spec = importlib.util.find_spec("opentelemetry.sdk.trace")
    resource_spec = importlib.util.find_spec("opentelemetry.sdk.resources")
    exporter_spec = importlib.util.find_spec("opentelemetry.sdk.trace.export")
    if sdk_trace_spec is None or resource_spec is None or exporter_spec is None:
        return

    from opentelemetry.sdk.resources import SERVICE_NAME, Resource  # type: ignore
    from opentelemetry.sdk.trace import TracerProvider  # type: ignore
    from opentelemetry.sdk.trace.export import (  # type: ignore
        BatchSpanProcessor,
        ConsoleSpanExporter,
    )

    resource = Resource(attributes={SERVICE_NAME: service_name})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    try:
        trace.set_tracer_provider(provider)
    except RuntimeError:  # pragma: no cover - provider already configured
        return


def _observe_latency(route_name: str, elapsed: float) -> None:
    REQUEST_LATENCY.labels(route=route_name).observe(elapsed)


def instrument_route(route_name: str):
    """Decorator to time requests and create trace spans."""

    def decorator(func: Callable[..., _T]):
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any):
                tracer = trace.get_tracer(__name__) if trace else None
                span_cm = (
                    tracer.start_as_current_span(route_name) if tracer else contextlib.nullcontext()
                )
                start = time.perf_counter()
                span = None
                try:
                    with span_cm as span:
                        result = await func(*args, **kwargs)
                except Exception as exc:
                    if span is not None:
                        span.record_exception(exc)
                        if Status is not None and StatusCode is not None:
                            span.set_status(Status(StatusCode.ERROR, str(exc)))
                    _observe_latency(route_name, time.perf_counter() - start)
                    raise
                else:
                    _observe_latency(route_name, time.perf_counter() - start)
                    return result

            return async_wrapper

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any):
            tracer = trace.get_tracer(__name__) if trace else None
            span_cm = (
                tracer.start_as_current_span(route_name) if tracer else contextlib.nullcontext()
            )
            start = time.perf_counter()
            span = None
            try:
                with span_cm as span:
                    result = func(*args, **kwargs)
            except Exception as exc:
                if span is not None:
                    span.record_exception(exc)
                    if Status is not None and StatusCode is not None:
                        span.set_status(Status(StatusCode.ERROR, str(exc)))
                _observe_latency(route_name, time.perf_counter() - start)
                raise
            else:
                _observe_latency(route_name, time.perf_counter() - start)
                return result

        return sync_wrapper

    return decorator


def record_llm_tokens(route_name: str, tokens: int) -> None:
    """Record the number of tokens processed by an endpoint."""

    LLM_TOKENS.labels(route=route_name).inc(tokens)


def _extract_route(request: Request) -> str:
    candidate: Any = request.scope.get("route")
    if candidate is not None:
        path = getattr(candidate, "path", None) or getattr(candidate, "name", None)
        if path:
            return str(path)
    return str(request.url.path)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Collect Prometheus metrics and correlate logs with request metadata."""

    def __init__(self, app):
        super().__init__(app)
        self._tracer = trace.get_tracer(__name__) if trace else None

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Any]]):
        method = request.method
        route = _extract_route(request)
        client_ip = request.client.host if request.client else None
        request_id = uuid.uuid4().hex
        context_token = bind_log_context(
            request_id=request_id,
            http_method=method,
            http_route=route,
            client_ip=client_ip,
        )
        status_token: Token[dict[str, Any]] | None = None
        status_code = 500
        start = time.perf_counter()
        span_cm = (
            self._tracer.start_as_current_span(f"{method} {route}")
            if self._tracer
            else contextlib.nullcontext()
        )
        span = None
        try:
            with span_cm as span:
                if span is not None:
                    span.set_attribute("http.method", method)
                    span.set_attribute("http.route", route)
                    span.set_attribute("http.target", str(request.url))
                    if client_ip:
                        span.set_attribute("http.client_ip", client_ip)
                response = await call_next(request)
                status_code = getattr(response, "status_code", 200)
        except Exception as exc:
            if span is not None:
                span.record_exception(exc)
                if Status is not None and StatusCode is not None:
                    span.set_status(Status(StatusCode.ERROR, str(exc)))
            status_code = 500
            status_token = bind_log_context(http_status=str(status_code))
            raise
        else:
            status_token = bind_log_context(http_status=str(status_code))
            return response
        finally:
            elapsed = time.perf_counter() - start
            labels = {
                "method": method,
                "route": route,
                "status": str(status_code),
            }
            HTTP_REQUEST_DURATION.labels(**labels).observe(elapsed)
            HTTP_REQUESTS.labels(**labels).inc()
            log_level = logging.WARNING if status_code >= 400 else logging.INFO
            logger.log(
                log_level,
                "request.completed",
                extra={
                    "duration_ms": round(elapsed * 1000, 3),
                    "status_code": status_code,
                },
            )
            if status_token is not None:
                reset_log_context(status_token)
            reset_log_context(context_token)


__all__ = [
    "HTTP_REQUESTS",
    "HTTP_REQUEST_DURATION",
    "LLM_TOKENS",
    "ObservabilityMiddleware",
    "REQUEST_LATENCY",
    "instrument_route",
    "record_llm_tokens",
    "setup_telemetry",
]
