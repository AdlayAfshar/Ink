import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from backend.app.core.config import Settings


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv(
        "CORS_ALLOWED_ORIGINS",
        "http://test-frontend.example.com",
    )

    test_settings = Settings()

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=test_settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return TestClient(app)


def test_cors_preflight_allows_configured_origin(client: TestClient):
    response = client.options(
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


def test_cors_preflight_rejects_unknown_origin(client: TestClient):
    response = client.options(
        "/health",
        headers={
            "Origin": "https://not-allowed.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers