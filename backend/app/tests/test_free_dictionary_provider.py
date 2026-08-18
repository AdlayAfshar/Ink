import httpx
import pytest

from backend.app.modules.dictionary.exceptions import (
    DictionaryProviderError,
    WordNotFoundError,
)
from backend.app.modules.dictionary.providers.free_dictionary import (
    FreeDictionaryProvider,
)


def create_provider(handler, timeout: float = 5.0) -> FreeDictionaryProvider:
    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)

    return FreeDictionaryProvider(
        base_url="https://dictionary.test/api/v2", timeout=timeout, client=client
    )


def test_lookup_returns_normalized_dictionary_entry():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v2/entries/en/example"

        return httpx.Response(
            status_code=200,
            json=[
                {
                    "word": "example",
                    "phonetic": "/ɪɡˈzɑːmpəl/",
                    "phonetics": [
                        {
                            "text": "/ɪɡˈzɑːmpəl/",
                            "audio": "https://audio.test/example.mp3",
                        }
                    ],
                    "meanings": [
                        {
                            "partOfSpeech": "noun",
                            "synonyms": ["sample"],
                            "antonyms": [],
                            "definitions": [
                                {
                                    "definition": (
                                        "Something representative of a group."
                                    ),
                                    "example": ("This is an example."),
                                    "synonyms": ["instance"],
                                    "antonyms": [],
                                }
                            ],
                        }
                    ],
                }
            ],
        )

    provider = create_provider(handler)

    result = provider.lookup("example")

    assert result.word == "example"
    assert result.phonetic == "/ɪɡˈzɑːmpəl/"
    assert result.audio_url == ("https://audio.test/example.mp3")

    assert len(result.definitions) == 1

    definition = result.definitions[0]

    assert definition.part_of_speech == "noun"
    assert definition.definition == ("Something representative of a group.")
    assert definition.example == "This is an example."
    assert definition.synonyms == ["sample", "instance"]
    assert definition.antonyms == []


def test_lookup_flattens_definitions_from_multiple_meanings():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json=[
                {
                    "word": "test",
                    "meanings": [
                        {
                            "partOfSpeech": "noun",
                            "definitions": [{"definition": "A procedure."}],
                        },
                        {
                            "partOfSpeech": "verb",
                            "definitions": [{"definition": ("To examine something.")}],
                        },
                    ],
                }
            ],
        )

    provider = create_provider(handler)

    result = provider.lookup("test")

    assert len(result.definitions) == 2

    assert result.definitions[0].part_of_speech == "noun"
    assert result.definitions[0].definition == "A procedure."

    assert result.definitions[1].part_of_speech == "verb"
    assert result.definitions[1].definition == ("To examine something.")


def test_lookup_raises_word_not_found_for_404():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=404,
            json={
                "title": "No Definitions Found",
                "message": ("Sorry, we could not find definitions for the word."),
            },
        )

    provider = create_provider(handler)

    with pytest.raises(WordNotFoundError, match="Word not found"):
        provider.lookup("not-a-real-word")


def test_lookup_raises_provider_error_for_server_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=500, json={"detail": "Internal server error"})

    provider = create_provider(handler)

    with pytest.raises(DictionaryProviderError, match="status code 500"):
        provider.lookup("example")


def test_lookup_raises_provider_error_for_network_failure():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Connection failed", request=request)

    provider = create_provider(handler)

    with pytest.raises(DictionaryProviderError, match="Could not connect"):
        provider.lookup("example")


def test_lookup_raises_provider_error_for_timeout():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("Request timed out", request=request)

    provider = create_provider(handler)

    with pytest.raises(DictionaryProviderError, match="timed out"):
        provider.lookup("example")


def test_lookup_raises_provider_error_for_invalid_json():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            content=b"not valid json",
            headers={"content-type": "application/json"},
        )

    provider = create_provider(handler)

    with pytest.raises(DictionaryProviderError, match="invalid JSON"):
        provider.lookup("example")


def test_lookup_raises_provider_error_when_no_definitions_exist():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json=[
                {
                    "word": "example",
                    "meanings": [],
                }
            ],
        )

    provider = create_provider(handler)

    with pytest.raises(DictionaryProviderError, match="no usable definitions"):
        provider.lookup("example")


def test_lookup_encodes_word_before_building_url():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == ("/api/v2/entries/en/ice cream")
        assert "%20" in str(request.url)

        return httpx.Response(
            status_code=200,
            json=[
                {
                    "word": "ice cream",
                    "meanings": [
                        {
                            "partOfSpeech": "noun",
                            "definitions": [{"definition": ("A frozen sweet food.")}],
                        }
                    ],
                }
            ],
        )

    provider = create_provider(handler)

    result = provider.lookup("ice cream")

    assert result.word == "ice cream"
