import pytest

from backend.app.modules.dictionary.exceptions import WordNotFoundError
from backend.app.modules.dictionary.providers import (
    DictionaryProvider,
    FakeDictionaryProvider,
)
from backend.app.modules.dictionary.schemas import DictionaryDefinition, DictionaryEntry


def use_dictionary_provider(provider: DictionaryProvider, word: str) -> DictionaryEntry:
    return provider.lookup(word)


def test_fake_provider_returns_dictionary_entry() -> None:
    provider = FakeDictionaryProvider()

    result = provider.lookup("book")

    assert isinstance(result, DictionaryEntry)
    assert result.word == "book"
    assert result.phonetic == "/fake/"
    assert result.audio_url == "https://example.com/audio.mp3"


def test_fake_provider_returns_definition() -> None:
    provider = FakeDictionaryProvider()

    result = provider.lookup("book")

    assert len(result.definitions) == 1

    definition = result.definitions[0]

    assert isinstance(definition, DictionaryDefinition)
    assert definition.part_of_speech == "noun"
    assert definition.definition == "A fake definition used for testing."
    assert definition.example == "This is only a test."
    assert definition.synonyms == ["sample", "mock"]
    assert definition.antonyms == ["real"]


def test_fake_provider_matches_dictionary_provider_protocol() -> None:
    provider = FakeDictionaryProvider()

    result = use_dictionary_provider(provider, "book")

    assert result.word == "book"


def test_fake_provider_raises_word_not_found_error() -> None:
    provider = FakeDictionaryProvider()

    with pytest.raises(WordNotFoundError):
        provider.lookup("missing")


def test_dictionary_definition_lists_are_not_shared() -> None:
    first_definition = DictionaryDefinition(definition="First definition")
    second_definition = DictionaryDefinition(definition="Second definition")

    first_definition.synonyms.append("example")

    assert first_definition.synonyms == ["example"]
    assert second_definition.synonyms == []
