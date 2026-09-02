from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.modules.dictionary.models import (
    Word,
    WordAntonym,
    WordDefinition,
    WordExample,
    WordSynonym,
)
from backend.app.modules.dictionary.providers.base import DictionaryProvider
from backend.app.modules.dictionary.schemas import DictionaryDefinition, DictionaryEntry


def normalize_word(word: str) -> str:
    return word.strip().lower()


def get_stored_word(db: Session, word: str) -> Word | None:
    """Return a stored English word matching the normalized lookup value."""
    normalized_word = normalize_word(word)

    return db.scalar(
        select(Word).where(Word.text == normalized_word, Word.language == "en")
    )


def dictionary_entry_from_word(word: Word) -> DictionaryEntry:
    """Convert a persisted Word and its related records into a DictionaryEntry."""
    definitions: list[DictionaryDefinition] = []

    for stored_definition in sorted(word.definitions, key=lambda item: item.position):
        example = None

        if stored_definition.examples:
            example = stored_definition.examples[0].example_text

        definitions.append(
            DictionaryDefinition(
                part_of_speech=stored_definition.part_of_speech,
                definition=stored_definition.definition,
                example=example,
                synonyms=[synonym.synonym for synonym in stored_definition.synonyms],
                antonyms=[antonym.antonym for antonym in stored_definition.antonyms],
            )
        )

    return DictionaryEntry(
        word=word.text,
        phonetic=word.phonetic,
        audio_url=word.audio_url,
        definitions=definitions,
    )


def persist_dictionary_entry(
    db: Session,
    entry: DictionaryEntry,
    provider_name: str,
) -> Word:
    """Persist a resolved dictionary entry and de-duplicate its related data."""
    normalized_word = normalize_word(entry.word)

    word = Word(
        text=normalized_word,
        language="en",
        provider=provider_name,
        provider_lookup_key=normalized_word,
        phonetic=entry.phonetic,
        audio_url=entry.audio_url,
    )

    db.add(word)
    db.flush()

    seen_definitions: set[tuple[str | None, str]] = set()
    position = 0

    for definition in entry.definitions:
        definition_key = (definition.part_of_speech, definition.definition)

        if definition_key in seen_definitions:
            continue

        seen_definitions.add(definition_key)

        stored_definition = WordDefinition(
            word_id=word.id,
            part_of_speech=definition.part_of_speech,
            definition=definition.definition,
            source=provider_name,
            position=position,
        )

        db.add(stored_definition)
        db.flush()

        position += 1

        if definition.example:
            db.add(
                WordExample(
                    word_id=word.id,
                    definition_id=stored_definition.id,
                    example_text=definition.example,
                    source=provider_name,
                )
            )

        seen_synonyms: set[str] = set()

        for synonym in definition.synonyms:
            normalized_synonym = normalize_word(synonym)

            if not normalized_synonym:
                continue

            if normalized_synonym in seen_synonyms:
                continue

            seen_synonyms.add(normalized_synonym)

            db.add(
                WordSynonym(
                    word_id=word.id,
                    definition_id=stored_definition.id,
                    synonym=normalized_synonym,
                )
            )

        seen_antonyms: set[str] = set()

        for antonym in definition.antonyms:
            normalized_antonym = normalize_word(antonym)

            if not normalized_antonym:
                continue

            if normalized_antonym in seen_antonyms:
                continue

            seen_antonyms.add(normalized_antonym)

            db.add(
                WordAntonym(
                    definition_id=stored_definition.id,
                    antonym=normalized_antonym,
                )
            )

    return word


def lookup_dictionary_entry(
    word: str,
    db: Session,
    provider: DictionaryProvider,
) -> DictionaryEntry:
    """Return cached dictionary data or resolve, persist, and return provider data."""
    normalized_word = normalize_word(word)

    stored_word = get_stored_word(db, normalized_word)

    if stored_word is not None:
        return dictionary_entry_from_word(stored_word)

    entry = provider.lookup(normalized_word)

    existing_word = get_stored_word(db, entry.word)

    if existing_word is not None:
        return dictionary_entry_from_word(existing_word)

    provider_name = provider.__class__.__name__

    try:
        persist_dictionary_entry(db=db, entry=entry, provider_name=provider_name)
        db.commit()
    except IntegrityError:
        db.rollback()

        stored_word = get_stored_word(db, entry.word)

        if stored_word is None:
            raise

        return dictionary_entry_from_word(stored_word)
    except Exception:
        db.rollback()
        raise

    stored_word = get_stored_word(db, entry.word)

    if stored_word is None:
        raise RuntimeError("Persisted dictionary entry could not be found")

    return dictionary_entry_from_word(stored_word)
