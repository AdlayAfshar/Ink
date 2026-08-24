from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Personal Glossary API"
    environment: str = "local"
    debug: bool = False
    database_url: str = "postgresql+psycopg:///ink"
    test_database_url: str = "postgresql+psycopg:///ink_test"

    jwt_secret_key: str = "development-only-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    dictionary_api_base_url: str = "https://api.dictionaryapi.dev/api/v2"

    dictionary_api_timeout: float = 5.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
