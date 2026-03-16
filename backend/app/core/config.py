from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "chatwoot-history"
    environment: str = "development"
    api_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/chatwoot_history"

    chatwoot_base_url: str = ""
    chatwoot_account_id: int = 1
    chatwoot_api_token: str = ""
    chatwoot_webhook_secret: str = ""


settings = Settings()
