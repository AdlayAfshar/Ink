from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as SQL_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base


class UserWord(Base):
    __tablename__ = "user_words"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "word_id",
            name="uq_user_words_user_id_word_id",
        ),
    )

    id: Mapped[str] = mapped_column(
        SQL_UUID(as_uuid=False),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    user_id: Mapped[str] = mapped_column(
        SQL_UUID(as_uuid=False),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    word_id: Mapped[str] = mapped_column(
        SQL_UUID(as_uuid=False),
        ForeignKey("words.id"),
        nullable=False,
        index=True,
    )
    learning_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="new",
    )
    saved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    last_reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    next_review_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    notes: Mapped[list["UserWordNote"]] = relationship(back_populates="user_word")


class UserWordNote(Base):
    __tablename__ = "user_word_notes"

    id: Mapped[str] = mapped_column(
        SQL_UUID(as_uuid=False),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    user_word_id: Mapped[str] = mapped_column(
        SQL_UUID(as_uuid=False),
        ForeignKey("user_words.id"),
        nullable=False,
        index=True,
    )
    note: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user_word: Mapped["UserWord"] = relationship(back_populates="notes")
