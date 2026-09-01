from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.modules.dictionary.dependencies import get_dictionary_provider
from backend.app.modules.dictionary.exceptions import (
    DictionaryProviderError,
    WordNotFoundError,
)
from backend.app.modules.dictionary.providers.base import DictionaryProvider
from backend.app.modules.dictionary.schemas import DictionaryEntry
from backend.app.modules.dictionary.service import lookup_dictionary_entry

router = APIRouter(prefix="/dictionary", tags=["dictionary"])

DbSession = Annotated[Session, Depends(get_db)]

DictionaryProviderDep = Annotated[DictionaryProvider, Depends(get_dictionary_provider)]


@router.get("/lookup/{word}", response_model=DictionaryEntry)
def lookup_word(
    word: str,
    provider: DictionaryProviderDep,
    db: DbSession,
) -> DictionaryEntry:
    try:
        return lookup_dictionary_entry(word=word, db=db, provider=provider)
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

