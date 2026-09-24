import importlib
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from backend.app import main
from backend.app.core import config


@pytest.fixture
def cors_client(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient, None, None]:
    monkeypatch.setenv(
        "CORS_ALLOWED_ORIGINS",
        "http://test-frontend.example.com",
    )

    importlib.reload(config)
    importlib.reload(main)

    with TestClient(main.app) as client:
        yield client

    monkeypatch.undo()
    importlib.reload(config)
    importlib.reload(main)


def test_cors_preflight_allows_configured_origin(
    cors_client: TestClient,
) -> None:
    response = cors_client.options(
        "/health",
        headers={
            "Origin": "http://test-frontend.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert (
        response.headers["access-control-allow-origin"]
        == "http://test-frontend.example.com"
    )


def test_cors_preflight_rejects_unknown_origin(
    cors_client: TestClient,
) -> None:
    response = cors_client.options(
        "/health",
        headers={
            "Origin": "https://not-allowed.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers