from __future__ import annotations

import os
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
    class attributes with defaults to instance attributes on construction and
    reading overrides from environment variables respecting ``model_config``
    options such as ``env_prefix``. Validation and type coercion are still
    intentionally omitted.
    """

    model_config: SettingsConfigDict

    def __init__(self, **values: Any) -> None:
        env_prefix = self._resolve_env_prefix()
        for name, attr in self.__class__.__dict__.items():
            if name.startswith("_") or name == "model_config":
                continue
            if callable(attr) or isinstance(attr, (classmethod, staticmethod)):
                continue
            if name in values:
                value = values[name]
            else:
                value = self._resolve_env_value(env_prefix, name)
                if value is None:
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

    @classmethod
    def _resolve_env_prefix(cls) -> str:
        config = getattr(cls, "model_config", None)
        if isinstance(config, dict):
            raw_prefix = config.get("env_prefix", "")
            if raw_prefix is None:
                return ""
            return str(raw_prefix)
        return ""

    @staticmethod
    def _resolve_env_value(env_prefix: str, field_name: str) -> Any | None:
        env_key = f"{env_prefix}{field_name}".upper()
        if env_key in os.environ:
            return os.environ[env_key]
        return None


__all__ = ["BaseSettings", "SettingsConfigDict"]
