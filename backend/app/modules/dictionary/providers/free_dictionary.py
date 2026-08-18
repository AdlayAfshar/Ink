from typing import Any
from urllib.parse import quote

import httpx
from pydantic import ValidationError

from backend.app.modules.dictionary.exceptions import (
    DictionaryProviderError,
    WordNotFoundError,
)
from backend.app.modules.dictionary.schemas import DictionaryDefinition, DictionaryEntry


class FreeDictionaryProvider:
    def __init__(
        self,
        base_url: str = "https://api.dictionaryapi.dev/api/v2",
        timeout: float = 5.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = client or httpx.Client()

    def lookup(self, word: str) -> DictionaryEntry:
        normalized_word = word.strip()

        if not normalized_word:
            raise WordNotFoundError("Word cannot be empty")

        encoded_word = quote(normalized_word, safe="")
        url = f"{self.base_url}/entries/en/{encoded_word}"

        try:
            response = self.client.get(url, timeout=self.timeout)
        except httpx.TimeoutException as exc:
            raise DictionaryProviderError(
                "Dictionary provider request timed out"
            ) from exc
        except httpx.RequestError as exc:
            raise DictionaryProviderError(
                "Could not connect to dictionary provider"
            ) from exc

        if response.status_code == 404:
            raise WordNotFoundError(f"Word not found: {normalized_word}")

        if response.status_code != 200:
            raise DictionaryProviderError(
                f"Dictionary provider returned status code {response.status_code}"
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise DictionaryProviderError(
                "Dictionary provider returned invalid JSON"
            ) from exc

        try:
            return self._normalize_response(
                payload=payload,
                requested_word=normalized_word,
            )
        except (TypeError, KeyError, ValidationError) as exc:
            raise DictionaryProviderError(
                "Dictionary provider returned an unexpected response"
            ) from exc

    def _normalize_response(self, payload: Any, requested_word: str) -> DictionaryEntry:
        if not isinstance(payload, list) or not payload:
            raise DictionaryProviderError(
                "Dictionary provider returned an empty response"
            )

        definitions: list[DictionaryDefinition] = []

        word = requested_word
        phonetic: str | None = None
        audio_url: str | None = None

        for entry_data in payload:
            if not isinstance(entry_data, dict):
                continue

            entry_word = entry_data.get("word")

            if isinstance(entry_word, str) and entry_word:
                word = entry_word

            if phonetic is None:
                phonetic = self._extract_phonetic(entry_data)

            if audio_url is None:
                audio_url = self._extract_audio_url(entry_data)

            meanings = entry_data.get("meanings", [])

            if not isinstance(meanings, list):
                continue

            for meaning in meanings:
                if not isinstance(meaning, dict):
                    continue

                part_of_speech = meaning.get("partOfSpeech")

                if not isinstance(part_of_speech, str):
                    part_of_speech = None

                meaning_synonyms = self._string_list(meaning.get("synonyms"))
                meaning_antonyms = self._string_list(meaning.get("antonyms"))

                raw_definitions = meaning.get("definitions", [])

                if not isinstance(raw_definitions, list):
                    continue

                for raw_definition in raw_definitions:
                    if not isinstance(raw_definition, dict):
                        continue

                    definition_text = raw_definition.get("definition")

                    if not isinstance(definition_text, str):
                        continue

                    definition_text = definition_text.strip()

                    if not definition_text:
                        continue

                    example = raw_definition.get("example")

                    if not isinstance(example, str):
                        example = None

                    synonyms = self._merge_unique(
                        meaning_synonyms,
                        self._string_list(raw_definition.get("synonyms")),
                    )

                    antonyms = self._merge_unique(
                        meaning_antonyms,
                        self._string_list(raw_definition.get("antonyms")),
                    )

                    definitions.append(
                        DictionaryDefinition(
                            part_of_speech=part_of_speech,
                            definition=definition_text,
                            example=example,
                            synonyms=synonyms,
                            antonyms=antonyms,
                        )
                    )

        if not definitions:
            raise DictionaryProviderError(
                "Dictionary provider returned no usable definitions"
            )

        return DictionaryEntry(
            word=word,
            phonetic=phonetic,
            audio_url=audio_url,
            definitions=definitions,
        )

    @staticmethod
    def _extract_phonetic(entry_data: dict[str, Any]) -> str | None:
        phonetic = entry_data.get("phonetic")

        if isinstance(phonetic, str) and phonetic.strip():
            return phonetic

        phonetics = entry_data.get("phonetics", [])

        if not isinstance(phonetics, list):
            return None

        for phonetic_data in phonetics:
            if not isinstance(phonetic_data, dict):
                continue

            text = phonetic_data.get("text")

            if isinstance(text, str) and text.strip():
                return text

        return None

    @staticmethod
    def _extract_audio_url(entry_data: dict[str, Any]) -> str | None:
        phonetics = entry_data.get("phonetics", [])

        if not isinstance(phonetics, list):
            return None

        for phonetic_data in phonetics:
            if not isinstance(phonetic_data, dict):
                continue

            audio = phonetic_data.get("audio")

            if isinstance(audio, str) and audio.strip():
                return audio

        return None

    @staticmethod
    def _string_list(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []

        return [
            item.strip() for item in value if isinstance(item, str) and item.strip()
        ]

    @staticmethod
    def _merge_unique(first: list[str], second: list[str]) -> list[str]:
        return list(dict.fromkeys(first + second))
