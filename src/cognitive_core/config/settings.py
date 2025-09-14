from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Cognitive Core Engine"
    api_prefix: str = "/api"
    debug: bool = False
    api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_prefix="COG_")
