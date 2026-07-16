from uuid import uuid4

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal, get_db
from backend.app.main import app
from backend.app.modules.auth.models import User
from backend.app.modules.auth.security import verify_password


@pytest.fixture
def db() -> Generator[Session, None, None]:
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()

        session.execute(
            delete(User).where(
                User.email.like("register-test-%@example.com")
            )
        )
        session.commit()
        session.close()


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def make_test_email() -> str:
    return f"register-test-{uuid4()}@example.com"


def test_register_user_returns_201(client: TestClient):
    email = make_test_email()

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "strong-password",
        },
    )

    assert response.status_code == 201


def test_register_user_returns_id_and_email(client: TestClient):
    email = make_test_email()

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "strong-password",
        },
    )

    data = response.json()

    assert response.status_code == 201
    assert data["id"] is not None
    assert data["email"] == email


def test_register_user_does_not_return_password_fields(
    client: TestClient,
):
    email = make_test_email()

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "strong-password",
        },
    )

    data = response.json()

    assert response.status_code == 201
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_user_stores_hashed_password(
    client: TestClient,
    db: Session,
):
    email = make_test_email()
    password = "strong-password"

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201

    user = db.scalar(
        select(User).where(User.email == email)
    )

    assert user is not None
    assert user.hashed_password != password
    assert verify_password(password, user.hashed_password) is True


def test_register_user_rejects_duplicate_email(
    client: TestClient,
):
    email = make_test_email()
    payload = {
        "email": email,
        "password": "strong-password",
    }

    first_response = client.post(
        "/auth/register",
        json=payload,
    )
    second_response = client.post(
        "/auth/register",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Email already registered"
    }