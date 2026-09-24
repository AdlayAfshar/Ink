from backend.app.core.config import settings
from backend.app.modules.dictionary.providers.base import DictionaryProvider
from backend.app.modules.dictionary.providers.free_dictionary import (
    FreeDictionaryProvider,
)
from backend.app.modules.dictionary.providers.merriam_webster import (
    MerriamWebsterProvider,
)


def get_dictionary_provider() -> DictionaryProvider:
    return FreeDictionaryProvider(
        base_url=settings.dictionary_api_base_url,
        timeout=settings.dictionary_api_timeout,
    )


def get_fallback_dictionary_provider() -> DictionaryProvider | None:
    if not settings.merriam_webster_api_key:
        return None

    return MerriamWebsterProvider(
        api_key=settings.merriam_webster_api_key,
        base_url=settings.merriam_webster_api_base_url,
        timeout=settings.merriam_webster_api_timeout,
    )