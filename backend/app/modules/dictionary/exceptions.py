class DictionaryProviderError(Exception):
    """Base exception for dictionary providers."""


class WordNotFoundError(DictionaryProviderError):
    """Raised when a word cannot be found."""