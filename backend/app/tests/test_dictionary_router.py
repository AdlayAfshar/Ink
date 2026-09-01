from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.modules.dictionary.dependencies import get_dictionary_provider
from backend.app.modules.dictionary.exceptions import DictionaryProviderError
from backend.app.modules.dictionary.models import (
    Word,
    WordAntonym,
    WordDefinition,
    WordExample,
    WordSynonym,
)
from backend.app.modules.dictionary.providers.fake import FakeDictionaryProvider
from backend.app.modules.dictionary.schemas import DictionaryDefinition, DictionaryEntry


class TrackingDictionaryProvider:
    def __init__(self) -> None:
        self.call_count = 0
        self.looked_up_words: list[str] = []

    def lookup(self, word: str) -> DictionaryEntry:
        self.call_count += 1
        self.looked_up_words.append(word)

        return DictionaryEntry(
            word=word,
            phonetic="/test/",
            audio_url="https://example.com/test.mp3",
            definitions=[
                DictionaryDefinition(
                    part_of_speech="noun",
                    definition="A test definition.",
                    example="This is a test example.",
                    synonyms=["sample", "example"],
                    antonyms=["real"],
                )
            ],
        )


class DuplicateDictionaryProvider:
    def __init__(self) -> None:
        self.call_count = 0

    def lookup(self, word: str) -> DictionaryEntry:
        self.call_count += 1

        definition = DictionaryDefinition(
            part_of_speech="noun",
            definition="A duplicate definition.",
            example="A duplicate example.",
            synonyms=["sample", "sample", "example"],
            antonyms=["real", "real", "genuine"],
        )

        return DictionaryEntry(
            word=word,
            definitions=[
                definition,
                definition,
            ],
        )


class FailingDictionaryProvider:
    def lookup(self, word: str) -> DictionaryEntry:
        raise DictionaryProviderError("Provider failed")


def test_lookup_word_returns_dictionary_entry(client: TestClient) -> None:
    app.dependency_overrides[get_dictionary_provider] = lambda: FakeDictionaryProvider()

    response = client.get("/dictionary/lookup/book")

    assert response.status_code == 200

    data = response.json()

    assert data["word"] == "book"
    assert data["phonetic"] == "/fake/"
    assert data["audio_url"] == "https://example.com/audio.mp3"
    assert len(data["definitions"]) == 1

    definition = data["definitions"][0]

    assert definition["part_of_speech"] == "noun"
    assert definition["definition"] == "A fake definition used for testing."
    assert definition["example"] == "This is only a test."
    assert set(definition["synonyms"]) == {"sample", "mock"}


def test_lookup_word_returns_404_when_word_not_found(client: TestClient) -> None:
    app.dependency_overrides[get_dictionary_provider] = lambda: FakeDictionaryProvider()

    response = client.get("/dictionary/lookup/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Word not found"}


def test_lookup_word_returns_502_when_provider_fails(client: TestClient) -> None:
    app.dependency_overrides[get_dictionary_provider] = lambda: (
        FailingDictionaryProvider()
    )

    response = client.get("/dictionary/lookup/book")

    assert response.status_code == 502
    assert response.json() == {"detail": "Dictionary provider unavailable"}


def test_dictionary_lookup_persists_provider_result(
    client: TestClient,
    db: Session,
) -> None:
    provider = TrackingDictionaryProvider()

    app.dependency_overrides[get_dictionary_provider] = lambda: provider

    response = client.get("/dictionary/lookup/book")

    assert response.status_code == 200
    assert provider.call_count == 1
    assert provider.looked_up_words == ["book"]

    word = db.scalar(select(Word).where(Word.text == "book", Word.language == "en"))

    assert word is not None
    assert word.provider == "TrackingDictionaryProvider"
    assert word.provider_lookup_key == "book"
    assert word.phonetic == "/test/"
    assert word.audio_url == "https://example.com/test.mp3"

    definition = db.scalar(
        select(WordDefinition).where(WordDefinition.word_id == word.id)
    )

    assert definition is not None
    assert definition.part_of_speech == "noun"
    assert definition.definition == "A test definition."
    assert definition.source == "TrackingDictionaryProvider"

    example = db.scalar(
        select(WordExample).where(WordExample.definition_id == definition.id)
    )

    assert example is not None
    assert example.example_text == "This is a test example."
    assert example.source == "TrackingDictionaryProvider"

    synonyms = db.scalars(
        select(WordSynonym).where(WordSynonym.definition_id == definition.id)
    ).all()

    assert {synonym.synonym for synonym in synonyms} == {"sample", "example"}

    antonyms = db.scalars(
        select(WordAntonym).where(WordAntonym.definition_id == definition.id)
    ).all()

    assert {antonym.antonym for antonym in antonyms} == {"real"}


def test_dictionary_lookup_uses_database_cache(client: TestClient) -> None:
    provider = TrackingDictionaryProvider()

    app.dependency_overrides[get_dictionary_provider] = lambda: provider

    first_response = client.get("/dictionary/lookup/book")
    second_response = client.get("/dictionary/lookup/book")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert provider.call_count == 1
    assert provider.looked_up_words == ["book"]

    data = second_response.json()

    assert data["word"] == "book"
    assert data["phonetic"] == "/test/"
    assert data["audio_url"] == "https://example.com/test.mp3"
    assert len(data["definitions"]) == 1

    definition = data["definitions"][0]

    assert definition["part_of_speech"] == "noun"
    assert definition["definition"] == "A test definition."
    assert definition["example"] == "This is a test example."
    assert set(definition["synonyms"]) == {"sample", "example"}
    assert definition["antonyms"] == ["real"]


def test_dictionary_lookup_normalizes_word_before_cache_lookup(
    client: TestClient,
    db: Session,
) -> None:
    provider = TrackingDictionaryProvider()

    app.dependency_overrides[get_dictionary_provider] = lambda: provider

    first_response = client.get("/dictionary/lookup/Book")
    second_response = client.get("/dictionary/lookup/book")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert provider.call_count == 1
    assert provider.looked_up_words == ["book"]

    word = db.scalar(select(Word))

    assert word is not None
    assert word.text == "book"
    assert word.provider_lookup_key == "book"


def test_dictionary_lookup_provider_failure_does_not_persist_data(
    client: TestClient,
    db: Session,
) -> None:
    provider = FailingDictionaryProvider()

    app.dependency_overrides[get_dictionary_provider] = lambda: provider

    response = client.get("/dictionary/lookup/failure")

    assert response.status_code == 502

    word = db.scalar(select(Word).where(Word.text == "failure"))

    assert word is None


def test_dictionary_lookup_is_idempotent(
    client: TestClient,
    db: Session,
) -> None:
    provider = TrackingDictionaryProvider()

    app.dependency_overrides[get_dictionary_provider] = lambda: provider

    first_response = client.get("/dictionary/lookup/book")
    second_response = client.get("/dictionary/lookup/book")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert provider.call_count == 1
    assert provider.looked_up_words == ["book"]

    word_count = db.scalar(select(func.count()).select_from(Word))

    definition_count = db.scalar(select(func.count()).select_from(WordDefinition))

    example_count = db.scalar(select(func.count()).select_from(WordExample))

    synonym_count = db.scalar(select(func.count()).select_from(WordSynonym))

    antonym_count = db.scalar(select(func.count()).select_from(WordAntonym))

    assert word_count == 1
    assert definition_count == 1
    assert example_count == 1
    assert synonym_count == 2
    assert antonym_count == 1


def test_dictionary_lookup_deduplicates_provider_data(
    client: TestClient,
    db: Session,
) -> None:
    provider = DuplicateDictionaryProvider()

    app.dependency_overrides[get_dictionary_provider] = lambda: provider

    response = client.get("/dictionary/lookup/book")

    assert response.status_code == 200
    assert provider.call_count == 1

    definition_count = db.scalar(select(func.count()).select_from(WordDefinition))

    example_count = db.scalar(select(func.count()).select_from(WordExample))

    synonym_count = db.scalar(select(func.count()).select_from(WordSynonym))

    antonym_count = db.scalar(select(func.count()).select_from(WordAntonym))

    assert definition_count == 1
    assert example_count == 1
    assert synonym_count == 2
    assert antonym_count == 2
