import httpx
import pytest

from backend.app.modules.dictionary.exceptions import (
    DictionaryProviderError,
    WordNotFoundError,
)
from backend.app.modules.dictionary.providers.merriam_webster import (
    MerriamWebsterProvider,
)


def test_lookup_returns_dictionary_entry() -> None:
    payload = [
        {
            "meta": {
                "id": "book:1",
            },
            "hwi": {
                "hw": "book",
                "prs": [
                    {
                        "ipa": "ˈbʊk",
                        "sound": {
                            "audio": "book0001",
                        },
                    }
                ],
            },
            "fl": "noun",
            "shortdef": [
                "a set of printed sheets of paper held together inside a cover",
                "a long written work that can be read on a computer",
            ],
        },
        {
            "meta": {
                "id": "book:2",
            },
            "hwi": {
                "hw": "book",
                "altprs": [
                    {
                        "ipa": "ˈbʊk",
                    }
                ],
            },
            "fl": "verb",
            "shortdef": [
                "to make arrangements to use or have something later",
            ],
        },
        {
            "meta": {
                "id": "book club",
            },
            "hwi": {
                "hw": "book club",
            },
            "fl": "noun",
            "shortdef": [
                "a group of people who meet to discuss books",
            ],
        },
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["key"] == "test-api-key"
        return httpx.Response(200, json=payload)

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
    )

    provider = MerriamWebsterProvider(
        api_key="test-api-key",
        client=client,
    )

    result = provider.lookup("book")

    assert result.word == "book"
    assert result.phonetic == "ˈbʊk"
    assert result.audio_url == (
        "https://media.merriam-webster.com/audio/prons/en/us/mp3/b/book0001.mp3"
    )

    assert len(result.definitions) == 3

    assert result.definitions[0].part_of_speech == "noun"
    assert result.definitions[0].definition == (
        "a set of printed sheets of paper held together inside a cover"
    )

    assert result.definitions[1].part_of_speech == "noun"
    assert result.definitions[1].definition == (
        "a long written work that can be read on a computer"
    )

    assert result.definitions[2].part_of_speech == "verb"
    assert result.definitions[2].definition == (
        "to make arrangements to use or have something later"
    )


def test_lookup_raises_word_not_found_when_no_exact_match() -> None:
    payload = [
        {
            "meta": {
                "id": "book club",
            },
            "fl": "noun",
            "shortdef": [
                "a group of people who meet to discuss books",
            ],
        }
    ]

    client = httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json=payload))
    )

    provider = MerriamWebsterProvider(
        api_key="test-api-key",
        client=client,
    )

    with pytest.raises(WordNotFoundError):
        provider.lookup("book")


def test_lookup_raises_provider_error_on_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout(
            "Request timed out",
            request=request,
        )

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
    )

    provider = MerriamWebsterProvider(
        api_key="test-api-key",
        client=client,
    )

    with pytest.raises(DictionaryProviderError):
        provider.lookup("book")


def test_lookup_raises_provider_error_on_request_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError(
            "Connection failed",
            request=request,
        )

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
    )

    provider = MerriamWebsterProvider(
        api_key="test-api-key",
        client=client,
    )

    with pytest.raises(DictionaryProviderError):
        provider.lookup("book")


def test_lookup_raises_provider_error_on_non_200_response() -> None:
    client = httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(500))
    )

    provider = MerriamWebsterProvider(
        api_key="test-api-key",
        client=client,
    )

    with pytest.raises(DictionaryProviderError):
        provider.lookup("book")


def test_lookup_raises_provider_error_on_invalid_json() -> None:
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                content=b"not-json",
            )
        )
    )

    provider = MerriamWebsterProvider(
        api_key="test-api-key",
        client=client,
    )

    with pytest.raises(DictionaryProviderError):
        provider.lookup("book")
