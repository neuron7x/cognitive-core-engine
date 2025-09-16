from __future__ import annotations

import json
from typing import Any, Iterable

from pydantic import Field, field_validator

try:  # pragma: no cover - allow operation without optional dependency
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ModuleNotFoundError:  # pragma: no cover - fallback shim
    from pydantic import BaseModel, ConfigDict

    class BaseSettings(BaseModel):
        model_config = ConfigDict()

    SettingsConfigDict = ConfigDict


class Settings(BaseSettings):
    app_name: str = "Cognitive Core Engine"
    api_prefix: str = "/api"
    debug: bool = False
    api_key: str = Field(
        default="",
        description=(
            "API key (or comma-separated keys) required for authenticating requests. "
            "Must be set via environment configuration before exposing the service."
        ),
    )
    rate_limit_rps: float = 5.0
    rate_limit_burst: int = 10
    allowed_origins: list[str] = Field(
        default_factory=list,
        description="List of allowed CORS origins for the public API.",
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _parse_allowed_origins(cls, value: Any) -> list[str]:
        if value is None:
            return []

        if isinstance(value, str):
            raw_value = value.strip()
            if not raw_value:
                return []

            try:
                parsed = json.loads(raw_value)
            except json.JSONDecodeError:
                candidates: Iterable[str] = raw_value.split(",")
            else:
                if isinstance(parsed, str):
                    candidates = [parsed]
                elif isinstance(parsed, Iterable):
                    candidates = parsed
                else:
                    raise TypeError("allowed_origins must be a string or iterable of strings")

            return [item.strip() for item in candidates if str(item).strip()]

        if isinstance(value, Iterable):
            return [str(item).strip() for item in value if str(item).strip()]

        return [str(value).strip()]

    model_config = SettingsConfigDict(env_file=".env", env_prefix="COG_")
