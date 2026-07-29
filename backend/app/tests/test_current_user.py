from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.modules.auth.models import User


def authorization_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_me_returns_current_user_for_valid_token(
    client: TestClient,
    make_test_email: Callable[[str], str],
    register_test_user: Callable[[str, str], dict],
    login_test_user: Callable[[str, str], str],
):
    email = make_test_email("current-user")
    password = "strong-password"

    registered_user = register_test_user(email, password)

    token = login_test_user(email, password)

    response = client.get("/auth/me", headers=authorization_header(token))

    assert response.status_code == 200
    assert response.json() == {"id": registered_user["id"], "email": email}


def test_me_returns_401_when_token_is_missing(client: TestClient):
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_returns_401_for_malformed_token(client: TestClient):
    response = client.get(
        "/auth/me", headers=authorization_header("this-is-not-a-valid-token")
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_returns_401_for_expired_token(client: TestClient):
    expired_token = jwt.encode(
        {
            "sub": str(uuid4()),
            "exp": datetime.now(UTC) - timedelta(minutes=1),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get("/auth/me", headers=authorization_header(expired_token))

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_returns_401_for_nonexistent_user(client: TestClient):
    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "exp": datetime.now(UTC) + timedelta(minutes=30),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get("/auth/me", headers=authorization_header(token))

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_returns_401_when_user_was_deleted(
    client: TestClient,
    db: Session,
    make_test_email: Callable[[str], str],
    register_test_user: Callable[[str, str], dict],
    login_test_user: Callable[[str, str], str],
):
    email = make_test_email("deleted-user")
    password = "strong-password"

    registered_user = register_test_user(email, password)

    token = login_test_user(email, password)

    user = db.get(User, registered_user["id"])

    assert user is not None

    db.delete(user)
    db.commit()

    response = client.get("/auth/me", headers=authorization_header(token))

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
    assert response.headers["www-authenticate"] == "Bearer"
