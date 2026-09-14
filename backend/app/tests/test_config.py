import pytest
from pydantic import ValidationError

from backend.app.core.config import DEVELOPMENT_JWT_SECRET, Settings


def test_settings_defaults():
    settings = Settings(_env_file=None)

    assert settings.app_name == "Personal Glossary API"
    assert settings.environment == "local"
    assert settings.database_url == "postgresql+psycopg:///ink"
    assert settings.jwt_secret_key == DEVELOPMENT_JWT_SECRET
    assert settings.cors_allowed_origins == [
        "http://localhost:3000",
        "http://localhost:5173",
    ]


def test_settings_override_from_env_vars(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "overridden_psql_url",
    )

    settings = Settings(_env_file=None)

    assert settings.database_url == "overridden_psql_url"


def test_production_rejects_development_jwt_secret():
    with pytest.raises(
        ValidationError,
        match="Production JWT_SECRET_KEY must be set",
    ):
        Settings(
            environment="production",
            database_url="postgresql+psycopg://user:password@db:5432/ink",
            cors_allowed_origins=["https://app.example.com"],
            _env_file=None,
        )


def test_cors_origins_parse_from_comma_separated_env(monkeypatch):
    monkeypatch.setenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173",
    )

    settings = Settings(_env_file=None)

    assert settings.cors_allowed_origins == [
        "http://localhost:3000",
        "http://localhost:5173",
    ]


def test_cors_origins_parse_from_json_env(monkeypatch):
    monkeypatch.setenv(
        "CORS_ALLOWED_ORIGINS",
        '["https://app.example.com", "https://admin.example.com"]',
    )

    settings = Settings(_env_file=None)

    assert settings.cors_allowed_origins == [
        "https://app.example.com",
        "https://admin.example.com",
    ]


def test_production_accepts_safe_configuration():
    settings = Settings(
        environment="production",
        database_url="postgresql+psycopg://user:password@db:5432/ink",
        jwt_secret_key="a-real-production-secret",
        cors_allowed_origins=["https://app.example.com"],
        _env_file=None,
    )

    assert settings.environment == "production"