"""Registry for UMAA+EPAUP metrics."""
from typing import Callable, Any, Dict

_REGISTRY: Dict[str, Callable[..., Any]] = {}


def register_metric(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to register a metric by name."""

    def wrapper(fn: Callable[..., Any]) -> Callable[..., Any]:
        _REGISTRY[name] = fn
        return fn

    return wrapper


def get(name: str) -> Callable[..., Any]:
    """Return a registered metric callable."""
    return _REGISTRY[name]


def list_metrics() -> list[str]:
    """List all registered metric names."""
    return sorted(_REGISTRY)
