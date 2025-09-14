from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "event_hub"
    app_env: str = "local"
    log_level: str = "INFO"
    prometheus_enabled: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")


settings = Settings()
