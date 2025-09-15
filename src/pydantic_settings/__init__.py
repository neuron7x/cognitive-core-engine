from __future__ import annotations

from typing import Any


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
            setattr(self, name, values.get(name, attr))


__all__ = ["BaseSettings", "SettingsConfigDict"]
