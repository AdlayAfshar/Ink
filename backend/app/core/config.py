from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Personal Glossary API"
    environment: str = "local"
    debug: bool = False
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ink"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()