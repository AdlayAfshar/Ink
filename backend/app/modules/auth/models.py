from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as SQL_UUID
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base



class User(Base):
    __tablename__ = "users"

    # Integer auto-increment primary key (traditional SQL approach).
    # id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Uses Python UUID objects (better type safety, slightly more serialization overhead). Requires: import uuid
    # id: Mapped[uuid.UUID] = mapped_column(
    #     SQL_UUID(as_uuid=True),
    #     primary_key=True,
    #     server_default=sa.text("gen_random_uuid()"),
    # )

    # Uses plain strings (simpler to work with in APIs while PostgreSQL still stores a UUID).
    id: Mapped[str] = mapped_column(
        SQL_UUID(as_uuid=False),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )