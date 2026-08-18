from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base


class Word(Base):
    __tablename__ = "words"
    __table_args__ = (
        UniqueConstraint("text", "language", name="uq_words_text_language"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(16), nullable=False, default="en")
    provider: Mapped[str | None] = mapped_column(String(100))
    provider_lookup_key: Mapped[str | None] = mapped_column(String(255))

    definitions: Mapped[list["WordDefinition"]] = relationship(back_populates="word")
    examples: Mapped[list["WordExample"]] = relationship(back_populates="word")
    synonyms: Mapped[list["WordSynonym"]] = relationship(back_populates="word")


class WordDefinition(Base):
    __tablename__ = "word_definitions"

    id: Mapped[int] = mapped_column(primary_key=True)
    word_id: Mapped[int] = mapped_column(
        ForeignKey("words.id"),
        nullable=False,
        index=True,
    )
    part_of_speech: Mapped[str | None] = mapped_column(String(50))
    definition: Mapped[str] = mapped_column(Text, nullable=False)

    word: Mapped["Word"] = relationship(back_populates="definitions")


class WordExample(Base):
    __tablename__ = "word_examples"

    id: Mapped[int] = mapped_column(primary_key=True)
    word_id: Mapped[int] = mapped_column(
        ForeignKey("words.id"),
        nullable=False,
        index=True,
    )
    example: Mapped[str] = mapped_column(Text, nullable=False)

    word: Mapped["Word"] = relationship(back_populates="examples")


class WordSynonym(Base):
    __tablename__ = "word_synonyms"

    id: Mapped[int] = mapped_column(primary_key=True)
    word_id: Mapped[int] = mapped_column(
        ForeignKey("words.id"),
        nullable=False,
        index=True,
    )
    synonym: Mapped[str] = mapped_column(String(255), nullable=False)

    word: Mapped["Word"] = relationship(back_populates="synonyms")
