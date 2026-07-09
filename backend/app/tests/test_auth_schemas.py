import pytest
from pydantic import ValidationError

from backend.app.modules.auth.schemas import Token, UserCreate, UserLogin, UserRead


def test_user_create_accepts_valid_data():
    user = UserCreate(
        email="user@example.com",
        password="valid-password",
    )

    assert user.email == "user@example.com"
    assert user.password == "valid-password"


def test_user_create_rejects_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            email="not-an-email",
            password="valid-password",
        )


def test_user_create_rejects_short_password():
    with pytest.raises(ValidationError):
        UserCreate(
            email="user@example.com",
            password="short",
        )


def test_user_read_excludes_hashed_password():
    user = UserRead(
        id=1,
        email="user@example.com",
    )

    data = user.model_dump()

    assert data == {
        "id": 1,
        "email": "user@example.com",
    }
    assert "hashed_password" not in data


def test_token_has_default_bearer_type():
    token = Token(access_token="fake-token")

    assert token.access_token == "fake-token"
    assert token.token_type == "bearer"


def test_user_login_accepts_valid_data():
    login = UserLogin(
        email="user@example.com",
        password="any-password",
    )

    assert login.email == "user@example.com"
    assert login.password == "any-password"