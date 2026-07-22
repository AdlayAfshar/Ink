from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Personal Glossary API"
    environment: str = "local"
    debug: bool = False
    # database_url: str = "postgresql+psycopg:///ink"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ink"

    jwt_secret_key: str = "development-only-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()