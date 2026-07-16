import os

from backend.app.core.config import Settings


def test_settings_defaults():
    settings = Settings()

    assert settings.app_name == "Personal Glossary API"
    assert settings.environment == "local"
    # assert settings.database_url == "postgresql+psycopg:///ink"
    # assert settings.database_url == "postgresql+psycopg://postgres:postgres@localhost:5432/ink"


def test_settings_override_from_env_vars():
    print(os.environ)
    os.environ["DATABASE_URL"] = "overridden_psql_url"

    settings = Settings()
    assert settings.database_url == "overridden_psql_url"