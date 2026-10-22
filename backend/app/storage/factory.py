from functools import lru_cache

from app.core.config import get_settings
from app.storage.azure_blob import AzureBlobStorage
from app.storage.base import FileStorage


@lru_cache
def get_storage() -> FileStorage | None:
    """Zwraca magazyn skonfigurowany zmiennymi środowiskowymi albo None, gdy go nie skonfigurowano."""
    settings = get_settings()
    if settings.storage_connection_string:
        return AzureBlobStorage(
            settings.storage_container,
            connection_string=settings.storage_connection_string.get_secret_value(),
        )
    if settings.storage_account_url:
        return AzureBlobStorage(settings.storage_container, account_url=settings.storage_account_url)
    return None
