from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.modules.dictionary.dependencies import get_dictionary_provider
from backend.app.modules.dictionary.exceptions import (
    DictionaryProviderError,
    WordNotFoundError,
)
from backend.app.modules.dictionary.providers.base import DictionaryProvider
from backend.app.modules.dictionary.schemas import DictionaryEntry

router = APIRouter(prefix="/dictionary", tags=["dictionary"])

DictionaryProviderDep = Annotated[DictionaryProvider, Depends(get_dictionary_provider)]


@router.get("/lookup/{word}", response_model=DictionaryEntry)
def lookup_word(word: str, provider: DictionaryProviderDep) -> DictionaryEntry:
    try:
        return provider.lookup(word)
    except WordNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found",
        ) from exc
    except DictionaryProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Dictionary provider unavailable",
        ) from exc
