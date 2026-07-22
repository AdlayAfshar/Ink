from uuid import uuid4

from jose import jwt

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.app.core.config import settings
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

def register_test_user(
    client: TestClient,
    email: str,
    password: str,
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


def test_register_user_returns_201_with_id_and_email(client: TestClient):
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

def test_login_with_valid_credentials_returns_token(
    client: TestClient,
):
    email = make_test_email()
    password = "strong-password"

    register_test_user(
        client=client,
        email=email,
        password=password,
    )

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["access_token"]
    assert data["token_type"] == "bearer"

def test_login_token_contains_subject_and_expiration(
    client: TestClient,
):
    email = make_test_email()
    password = "strong-password"

    registered_user = register_test_user(
        client=client,
        email=email,
        password=password,
    )

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    token = response.json()["access_token"]

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    assert payload["sub"] == registered_user["id"]
    assert "exp" in payload

def test_login_with_wrong_password_returns_401(
    client: TestClient,
):
    email = make_test_email()

    register_test_user(
        client=client,
        email=email,
        password="correct-password",
    )

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid credentials"
    }

def test_login_with_unknown_email_returns_401(
    client: TestClient,
):
    response = client.post(
        "/auth/login",
        json={
            "email": make_test_email(),
            "password": "strong-password",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid credentials"
    }


def test_login_response_does_not_expose_password_data(
    client: TestClient,
):
    email = make_test_email()
    password = "strong-password"

    register_test_user(
        client=client,
        email=email,
        password=password,
    )

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert set(data.keys()) == {
        "access_token",
        "token_type",
    }
    assert "password" not in data
    assert "hashed_password" not in data