import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.modules.dictionary.dependencies import get_dictionary_provider
from backend.app.modules.dictionary.exceptions import DictionaryProviderError
from backend.app.modules.dictionary.providers.fake import FakeDictionaryProvider
from backend.app.modules.dictionary.schemas import DictionaryEntry


class FailingDictionaryProvider:
    def lookup(self, word: str) -> DictionaryEntry:
        raise DictionaryProviderError("Provider failed")


@pytest.fixture
def dictionary_client():
    app.dependency_overrides[get_dictionary_provider] = lambda: FakeDictionaryProvider()

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.pop(get_dictionary_provider, None)


def test_lookup_word_returns_dictionary_entry(dictionary_client):
    response = dictionary_client.get("/dictionary/lookup/book")

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
    assert definition["synonyms"] == ["sample", "mock"]
    assert definition["antonyms"] == ["real"]


def test_lookup_word_returns_404_when_word_not_found(dictionary_client):
    response = dictionary_client.get("/dictionary/lookup/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Word not found"}


def test_lookup_word_returns_502_when_provider_fails():
    app.dependency_overrides[get_dictionary_provider] = lambda: (
        FailingDictionaryProvider()
    )

    try:
        with TestClient(app) as client:
            response = client.get("/dictionary/lookup/book")

        assert response.status_code == 502
        assert response.json() == {"detail": "Dictionary provider unavailable"}
    finally:
        app.dependency_overrides.pop(get_dictionary_provider, None)
