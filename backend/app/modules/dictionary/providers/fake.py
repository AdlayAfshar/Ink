from backend.app.modules.dictionary.exceptions import WordNotFoundError
from backend.app.modules.dictionary.schemas import DictionaryDefinition, DictionaryEntry


class FakeDictionaryProvider:
    def lookup(self, word: str) -> DictionaryEntry:
        if word == "missing":
            raise WordNotFoundError(f"Word '{word}' was not found.")

        return DictionaryEntry(
            word=word,
            phonetic="/fake/",
            audio_url="https://example.com/audio.mp3",
            definitions=[
                DictionaryDefinition(
                    part_of_speech="noun",
                    definition="A fake definition used for testing.",
                    example="This is only a test.",
                    synonyms=["sample", "mock"],
                    antonyms=["real"],
                )
            ],
        )
