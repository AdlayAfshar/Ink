from collections.abc import Callable, Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal, get_db
from backend.app.main import app
from backend.app.modules.auth.models import User


@pytest.fixture
def db() -> Generator[Session, None, None]:
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()

        session.execute(
            delete(User).where(
                User.email.like("%-test-%@example.com")
            )
        )

        session.commit()
        session.close()


@pytest.fixture
def client(
    db: Session,
) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def make_test_email() -> Callable[[str], str]:
    def _make_test_email(prefix: str = "auth") -> str:
        return f"{prefix}-test-{uuid4()}@example.com"

    return _make_test_email


@pytest.fixture
def register_test_user(
    client: TestClient,
) -> Callable[[str, str], dict]:
    def _register_test_user(
        email: str,
        password: str = "strong-password",
    ) -> dict:
        response = client.post(
            "/auth/register",
            json={
                "email": email,
                "password": password,
            },
        )

        assert response.status_code == 201

        return response.json()

    return _register_test_user


@pytest.fixture
def login_test_user(
    client: TestClient,
) -> Callable[[str, str], str]:
    def _login_test_user(
        email: str,
        password: str = "strong-password",
    ) -> str:
        response = client.post(
            "/auth/login",
            json={
                "email": email,
                "password": password,
            },
        )

        assert response.status_code == 200

        return response.json()["access_token"]

    return _login_test_user