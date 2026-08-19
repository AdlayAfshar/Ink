from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as SQL_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base


class Word(Base):
    __tablename__ = "words"
    __table_args__ = (
        UniqueConstraint("text", "language", name="uq_words_text_language"),
    )

    id: Mapped[str] = mapped_column(
        SQL_UUID(as_uuid=False),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    text: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    language: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="en",
        server_default="en",
    )
    provider: Mapped[str | None] = mapped_column(String(100), nullable=True)
    provider_lookup_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
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

    definitions: Mapped[list["WordDefinition"]] = relationship(back_populates="word")
    examples: Mapped[list["WordExample"]] = relationship(back_populates="word")
    synonyms: Mapped[list["WordSynonym"]] = relationship(back_populates="word")


class WordDefinition(Base):
    __tablename__ = "word_definitions"

    id: Mapped[str] = mapped_column(
        SQL_UUID(as_uuid=False),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    word_id: Mapped[str] = mapped_column(
        SQL_UUID(as_uuid=False),
        ForeignKey("words.id"),
        nullable=False,
        index=True,
    )
    part_of_speech: Mapped[str | None] = mapped_column(String(50), nullable=True)
    definition: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
        server_default="0",
    )
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    word: Mapped["Word"] = relationship(back_populates="definitions")
    examples: Mapped[list["WordExample"]] = relationship(back_populates="definition")
    synonyms: Mapped[list["WordSynonym"]] = relationship(back_populates="definition")


class WordExample(Base):
    __tablename__ = "word_examples"

    id: Mapped[str] = mapped_column(
        SQL_UUID(as_uuid=False),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    word_id: Mapped[str] = mapped_column(
        SQL_UUID(as_uuid=False),
        ForeignKey("words.id"),
        nullable=False,
        index=True,
    )
    definition_id: Mapped[str | None] = mapped_column(
        SQL_UUID(as_uuid=False),
        ForeignKey("word_definitions.id"),
        nullable=True,
    )
    example_text: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)

    word: Mapped["Word"] = relationship(back_populates="examples")
    definition: Mapped["WordDefinition | None"] = relationship(
        back_populates="examples"
    )


class WordSynonym(Base):
    __tablename__ = "word_synonyms"
    __table_args__ = (
        UniqueConstraint(
            "definition_id",
            "synonym",
            name="uq_word_synonyms_definition_id_synonym",
        ),
    )

    id: Mapped[str] = mapped_column(
        SQL_UUID(as_uuid=False),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    word_id: Mapped[str] = mapped_column(
        SQL_UUID(as_uuid=False),
        ForeignKey("words.id"),
        nullable=False,
        index=True,
    )
    definition_id: Mapped[str | None] = mapped_column(
        SQL_UUID(as_uuid=False),
        ForeignKey("word_definitions.id"),
        nullable=True,
    )
    synonym: Mapped[str] = mapped_column(String(255), nullable=False)

    word: Mapped["Word"] = relationship(back_populates="synonyms")
    definition: Mapped["WordDefinition | None"] = relationship(
        back_populates="synonyms"
    )


#  Log in to PostgreSQL => terminal: psql ink
#  View the current Alembic value => SQL: SELECT * FROM alembic_version;
