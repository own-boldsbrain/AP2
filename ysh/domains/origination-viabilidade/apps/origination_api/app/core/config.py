from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "YSH Origination API"
    api_prefix: str = "/v1"
    database_url: str
    nats_url: str = "nats://localhost:4222"
    jwt_public_key_base64: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
