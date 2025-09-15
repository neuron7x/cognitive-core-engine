from __future__ import annotations

from typing import Any, Callable

try:  # pragma: no cover - optional dependency hints
    from pydantic.fields import FieldInfo  # type: ignore
except Exception:  # pragma: no cover - field introspection fallback
    FieldInfo = None  # type: ignore


class SettingsConfigDict(dict[str, Any]):
    """Lightweight stand-in for :class:`pydantic_settings.SettingsConfigDict`."""


class BaseSettings:
    """Minimal replacement for :class:`pydantic_settings.BaseSettings`.

    This stub implements only the behaviour required by the test-suite: mapping
    class attributes with defaults to instance attributes on construction.
    Environment loading and validation are intentionally omitted.
    """

    model_config: SettingsConfigDict

    def __init__(self, **values: Any) -> None:
        for name, attr in self.__class__.__dict__.items():
            if name.startswith("_") or name == "model_config":
                continue
            if callable(attr) or isinstance(attr, (classmethod, staticmethod)):
                continue
            if name in values:
                value = values[name]
            else:
                value = self._resolve_default(attr)
            setattr(self, name, value)

    @staticmethod
    def _resolve_default(attr: Any) -> Any:
        if FieldInfo is not None and isinstance(attr, FieldInfo):  # pragma: no branch
            if attr.default_factory is not None:
                factory: Callable[[], Any] = attr.default_factory  # type: ignore[assignment]
                return factory()
            if attr.default is not None:
                return attr.default
            return None

        default_factory = getattr(attr, "default_factory", None)
        if callable(default_factory):
            return default_factory()

        default = getattr(attr, "default", attr)
        return default


__all__ = ["BaseSettings", "SettingsConfigDict"]
