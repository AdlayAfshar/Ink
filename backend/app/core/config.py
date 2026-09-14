import json
from typing import Annotated, Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

DEVELOPMENT_JWT_SECRET = "development-only-secret-key"
LOCAL_DATABASE_URL = "postgresql+psycopg:///ink"
LOCAL_CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5173"]


class Settings(BaseSettings):
    app_name: str = "Personal Glossary API"
    environment: Literal["local", "test", "production"] = "local"
    debug: bool = False

    database_url: str = LOCAL_DATABASE_URL
    test_database_url: str = "postgresql+psycopg:///ink_test"

    jwt_secret_key: str = DEVELOPMENT_JWT_SECRET
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    cors_allowed_origins: Annotated[list[str], NoDecode] = LOCAL_CORS_ORIGINS

    dictionary_api_base_url: str = "https://api.dictionaryapi.dev/api/v2"
    dictionary_api_timeout: float = 5.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors_allowed_origins(cls, value: object) -> object:
        if not isinstance(value, str):
            return value

        value = value.strip()

        if not value:
            return []

        if value.startswith("["):
            parsed = json.loads(value)

            if not isinstance(parsed, list):
                raise ValueError("CORS_ALLOWED_ORIGINS must be a list of origins")

            return parsed

        return [origin.strip() for origin in value.split(",") if origin.strip()]

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.environment != "production":
            return self

        if self.jwt_secret_key == DEVELOPMENT_JWT_SECRET:
            raise ValueError("Production JWT_SECRET_KEY must be set")

        if self.database_url == LOCAL_DATABASE_URL:
            raise ValueError("Production DATABASE_URL must be set")

        if self.debug:
            raise ValueError("DEBUG must be false in production")

        if not self.cors_allowed_origins:
            raise ValueError("Production CORS_ALLOWED_ORIGINS must be set")

        if "*" in self.cors_allowed_origins:
            raise ValueError("Wildcard CORS origin is not allowed in production")

        if any(origin in LOCAL_CORS_ORIGINS for origin in self.cors_allowed_origins):
            raise ValueError("Production CORS_ALLOWED_ORIGINS cannot use local origins")

        return self


settings = Settings()
