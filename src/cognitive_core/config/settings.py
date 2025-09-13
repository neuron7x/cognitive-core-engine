from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Cognitive Core Engine"
    api_prefix: str = "/api"
    debug: bool = False
    api_keys: list[str] | None = None

    @field_validator("api_keys", mode="before")
    @classmethod
    def split_api_keys(cls, v: str | list[str] | None) -> list[str] | None:
        if isinstance(v, str):
            if v == "":
                return [""]
            return [k.strip() for k in v.split(",")]
        return v

    model_config = SettingsConfigDict(env_file=".env", env_prefix="COG_")
