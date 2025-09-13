from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Cognitive Core Engine"
    api_prefix: str = "/api"
    debug: bool = False
    api_key: str | None = None
    rate_limit_rps: float = 5.0
    rate_limit_burst: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_prefix="COG_")
