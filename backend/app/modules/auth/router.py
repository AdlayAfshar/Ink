from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.modules.auth.dependencies import get_current_user
from backend.app.modules.auth.models import User
from backend.app.modules.auth.schemas import Token, UserCreate, UserRead
from backend.app.modules.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: DbSession) -> User:
    existing_user = db.scalar(select(User).where(User.email == str(payload.email)))

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        email=str(payload.email), hashed_password=hash_password(payload.password)
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from None

    db.refresh(user)

    return user


@router.post("/login", response_model=Token)
def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
) -> Token:
    user = db.scalar(select(User).where(User.email == form_data.username))

    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    access_token = create_access_token(subject=user.id, expires_delta=expires_delta)

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserRead)
def read_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user
