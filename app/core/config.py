from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # app
    app_name: str = "event-hub"
    app_env: str = "local"
    log_level: str = "INFO"
    prometheus_enabled: bool = True

    # clickhouse
    ch_host: str = "clickhouse"    # ⬅️ вместо URL
    ch_port: int = 8123
    ch_secure: bool = False       # True для https
    ch_database: str = "eventhub"
    ch_user: str | None = None
    ch_password: str | None = None
    ch_connect_timeout: float = 5.0
    ch_send_receive_timeout: float = 30.0

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")


settings = Settings()
