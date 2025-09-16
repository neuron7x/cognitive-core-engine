from __future__ import annotations

import contextlib
import contextvars
import importlib.util
import json
import logging
import logging.config
from datetime import datetime, timezone
from typing import Any

_LOG_CONTEXT: contextvars.ContextVar[dict[str, Any]] = contextvars.ContextVar(
    "log_context", default={}
)

_DEFAULT_RECORD_FIELDS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
}

_TRACE_SPEC = None
if importlib.util.find_spec("opentelemetry") is not None:
    _TRACE_SPEC = importlib.util.find_spec("opentelemetry.trace")

if _TRACE_SPEC is not None:  # pragma: no branch - dependency optional
    from opentelemetry import trace  # type: ignore
else:  # pragma: no cover - executed when optional dependency missing
    trace = None  # type: ignore[assignment]


def _stringify(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_stringify(item) for item in value]
    if isinstance(value, dict):
        return {str(k): _stringify(v) for k, v in value.items()}
    return repr(value)


def get_log_context() -> dict[str, Any]:
    return dict(_LOG_CONTEXT.get({}))


def bind_log_context(**kwargs: Any) -> contextvars.Token[dict[str, Any]]:
    current = get_log_context()
    for key, value in kwargs.items():
        if value is not None:
            current[str(key)] = value
    return _LOG_CONTEXT.set(current)


def reset_log_context(token: contextvars.Token[dict[str, Any]]) -> None:
    _LOG_CONTEXT.reset(token)


class StructuredLogFormatter(logging.Formatter):
    """Render log records as JSON with OpenTelemetry correlation."""

    def format(self, record: logging.LogRecord) -> str:
        log_record: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        context = get_log_context()
        if context:
            log_record.update(context)

        if trace is not None:
            span = trace.get_current_span()
            if span is not None:
                span_context = span.get_span_context()
                if getattr(span_context, "is_valid", False):
                    log_record["trace_id"] = format(span_context.trace_id, "032x")
                    log_record["span_id"] = format(span_context.span_id, "016x")

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            log_record["stack"] = self.formatStack(record.stack_info)

        extras = {
            key: _stringify(value)
            for key, value in record.__dict__.items()
            if key not in _DEFAULT_RECORD_FIELDS
        }
        if extras:
            log_record.update(extras)

        return json.dumps(log_record, ensure_ascii=False)


def _resolve_level(level: str | int) -> int:
    if isinstance(level, int):
        return level
    if isinstance(level, str):
        candidate = logging.getLevelName(level.upper())
        if isinstance(candidate, int):
            return candidate
    return logging.INFO


def setup_logging(level: str = "INFO") -> None:
    """Configure structured logging for the application."""

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "structured": {
                    "()": "cognitive_core.utils.logging.StructuredLogFormatter",
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "structured",
                    "level": _resolve_level(level),
                }
            },
            "root": {
                "level": _resolve_level(level),
                "handlers": ["default"],
            },
        }
    )
    logging.captureWarnings(True)


@contextlib.contextmanager
def log_context(**kwargs: Any):
    token = bind_log_context(**kwargs)
    try:
        yield
    finally:
        reset_log_context(token)


__all__ = [
    "StructuredLogFormatter",
    "bind_log_context",
    "get_log_context",
    "log_context",
    "reset_log_context",
    "setup_logging",
]
