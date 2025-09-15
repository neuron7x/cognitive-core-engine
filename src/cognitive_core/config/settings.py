from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    model_config = SettingsConfigDict(env_file=".env", env_prefix="COG_")
