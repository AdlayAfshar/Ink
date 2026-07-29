from typing import Protocol

from backend.app.modules.dictionary.schemas import DictionaryEntry


class DictionaryProvider(Protocol):
    def lookup(self, word: str) -> DictionaryEntry:
        ...