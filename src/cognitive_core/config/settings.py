from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Cognitive Core Engine"
    api_prefix: str = "/api"
    debug: bool = False
    api_key: str | None = None
    api_keys: list[str] | None = None

    @staticmethod
    def _split_csv(value: str | list[str] | None) -> list[str] | None:
        if value is None:
            return None
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value

    @classmethod
    def model_validate(cls, data):
        data = dict(data or {})
        data["api_keys"] = cls._split_csv(data.get("api_keys"))
        return super().model_validate(data)

    model_config = SettingsConfigDict(env_file=".env", env_prefix="COG_")
