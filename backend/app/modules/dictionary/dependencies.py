from backend.app.core.config import settings
from backend.app.modules.dictionary.providers.base import DictionaryProvider
from backend.app.modules.dictionary.providers.free_dictionary import (
    FreeDictionaryProvider,
)


def get_dictionary_provider() -> DictionaryProvider:
    return FreeDictionaryProvider(
        base_url=settings.dictionary_api_base_url,
        timeout=settings.dictionary_api_timeout,
    )