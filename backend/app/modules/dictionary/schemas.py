from pydantic import BaseModel, Field


class DictionaryDefinition(BaseModel):
    part_of_speech: str | None = None
    definition: str
    example: str | None = None
    synonyms: list[str] = Field(default_factory=list)
    antonyms: list[str] = Field(default_factory=list)


class DictionaryEntry(BaseModel):
    word: str
    phonetic: str | None = None
    audio_url: str | None = None
    definitions: list[DictionaryDefinition] = Field(default_factory=list)
