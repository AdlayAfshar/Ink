import logging
import re
from typing import Any
from urllib.parse import quote

import httpx
from pydantic import ValidationError

from backend.app.modules.dictionary.exceptions import (
    DictionaryProviderError,
    WordNotFoundError,
)
from backend.app.modules.dictionary.schemas import DictionaryDefinition, DictionaryEntry

logger = logging.getLogger(__name__)


class MerriamWebsterProvider:
    def __init__(
        self,
        api_key: str,
        base_url: str = (
            "https://www.dictionaryapi.com/api/v3/references/learners/json"
        ),
        timeout: float = 5.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = client or httpx.Client()

    def lookup(self, word: str) -> DictionaryEntry:
        normalized_word = word.strip()

        if not normalized_word:
            raise WordNotFoundError("Word cannot be empty")

        encoded_word = quote(normalized_word, safe="")
        url = f"{self.base_url}/{encoded_word}"

        try:
            response = self.client.get(
                url,
                params={"key": self.api_key},
                timeout=self.timeout,
            )
        except httpx.TimeoutException as exc:
            logger.warning(
                "Merriam-Webster provider timeout word=%s",
                normalized_word,
            )
            raise DictionaryProviderError(
                "Dictionary provider request timed out"
            ) from exc
        except httpx.RequestError as exc:
            logger.error(
                "Merriam-Webster provider request failed "
                "word=%s error_type=%s",
                normalized_word,
                type(exc).__name__,
            )
            raise DictionaryProviderError(
                "Could not connect to dictionary provider"
            ) from exc

        if response.status_code != 200:
            logger.error(
                "Merriam-Webster provider returned unexpected status "
                "word=%s status_code=%s",
                normalized_word,
                response.status_code,
            )
            raise DictionaryProviderError(
                f"Dictionary provider returned status code {response.status_code}"
            )

        try:
            payload = response.json()
        except ValueError as exc:
            logger.error(
                "Merriam-Webster provider returned invalid JSON word=%s",
                normalized_word,
            )
            raise DictionaryProviderError(
                "Dictionary provider returned invalid JSON"
            ) from exc

        try:
            return self._normalize_response(
                payload=payload,
                requested_word=normalized_word,
            )
        except WordNotFoundError:
            raise
        except DictionaryProviderError:
            logger.error(
                "Merriam-Webster response could not be normalized word=%s",
                normalized_word,
            )
            raise
        except (TypeError, KeyError, ValidationError) as exc:
            logger.error(
                "Merriam-Webster provider returned unexpected response "
                "word=%s error_type=%s",
                normalized_word,
                type(exc).__name__,
            )
            raise DictionaryProviderError(
                "Dictionary provider returned an unexpected response"
            ) from exc

    def _normalize_response(
        self,
        payload: Any,
        requested_word: str,
    ) -> DictionaryEntry:
        if not isinstance(payload, list) or not payload:
            raise WordNotFoundError(f"Word not found: {requested_word}")

        matching_entries = [
            entry
            for entry in payload
            if isinstance(entry, dict)
            and self._matches_requested_word(entry, requested_word)
        ]

        if not matching_entries:
            raise WordNotFoundError(f"Word not found: {requested_word}")

        definitions: list[DictionaryDefinition] = []
        phonetic: str | None = None
        audio_url: str | None = None

        for entry in matching_entries:
            if phonetic is None:
                phonetic = self._extract_phonetic(entry)

            if audio_url is None:
                audio_url = self._extract_audio_url(entry)

            part_of_speech = entry.get("fl")

            if not isinstance(part_of_speech, str):
                part_of_speech = None

            short_definitions = entry.get("shortdef", [])

            if not isinstance(short_definitions, list):
                continue

            for definition_text in short_definitions:
                if not isinstance(definition_text, str):
                    continue

                definition_text = self._clean_text(definition_text)

                if not definition_text:
                    continue

                definitions.append(
                    DictionaryDefinition(
                        part_of_speech=part_of_speech,
                        definition=definition_text,
                        example=None,
                        synonyms=[],
                        antonyms=[],
                    )
                )

        if not definitions:
            raise DictionaryProviderError(
                "Dictionary provider returned no usable definitions"
            )

        return DictionaryEntry(
            word=requested_word,
            phonetic=phonetic,
            audio_url=audio_url,
            definitions=definitions,
        )

    @staticmethod
    def _matches_requested_word(
        entry: dict[str, Any],
        requested_word: str,
    ) -> bool:
        meta = entry.get("meta")

        if not isinstance(meta, dict):
            return False

        entry_id = meta.get("id")

        if not isinstance(entry_id, str):
            return False

        headword = entry_id.split(":", maxsplit=1)[0]

        return headword.casefold() == requested_word.casefold()

    @staticmethod
    def _extract_phonetic(entry: dict[str, Any]) -> str | None:
        hwi = entry.get("hwi")

        if not isinstance(hwi, dict):
            return None

        pronunciations = hwi.get("prs")

        if not isinstance(pronunciations, list):
            pronunciations = hwi.get("altprs", [])

        if not isinstance(pronunciations, list):
            return None

        for pronunciation in pronunciations:
            if not isinstance(pronunciation, dict):
                continue

            ipa = pronunciation.get("ipa")

            if isinstance(ipa, str) and ipa.strip():
                return ipa.strip()

        return None

    @classmethod
    def _extract_audio_url(cls, entry: dict[str, Any]) -> str | None:
        hwi = entry.get("hwi")

        if not isinstance(hwi, dict):
            return None

        pronunciations = hwi.get("prs", [])

        if not isinstance(pronunciations, list):
            return None

        for pronunciation in pronunciations:
            if not isinstance(pronunciation, dict):
                continue

            sound = pronunciation.get("sound")

            if not isinstance(sound, dict):
                continue

            audio = sound.get("audio")

            if isinstance(audio, str) and audio.strip():
                return cls._build_audio_url(audio.strip())

        return None

    @staticmethod
    def _build_audio_url(audio: str) -> str:
        if audio.startswith("bix"):
            subdirectory = "bix"
        elif audio.startswith("gg"):
            subdirectory = "gg"
        elif audio[0].isdigit() or audio[0] in "_-":
            subdirectory = "number"
        else:
            subdirectory = audio[0]

        return (
            "https://media.merriam-webster.com/audio/prons/"
            f"en/us/mp3/{subdirectory}/{audio}.mp3"
        )

    @staticmethod
    def _clean_text(text: str) -> str:
        text = text.replace("{bc}", ": ")
        text = re.sub(r"\{/?[^{}]+\}", "", text)
        return " ".join(text.split()).strip(" :")