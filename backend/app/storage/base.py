import logging
from typing import BinaryIO, Protocol

from app.core.exceptions import StorageError

logger = logging.getLogger(__name__)


class FileStorage(Protocol):
    """Interfejs magazynu plików. Implementacja produkcyjna: Azure Blob Storage."""

    def upload(self, key: str, fileobj: BinaryIO) -> None: ...

    def delete(self, key: str) -> None: ...

    def download_url(self, key: str, filename: str, expires_in: int) -> str: ...


def delete_quietly(storage: FileStorage, key: str) -> None:
    """Usuwa obiekt, a błąd tylko loguje. Używane po zapisie w bazie, gdy nie wolno już zgłaszać błędu."""
    try:
        storage.delete(key)
    except StorageError:
        logger.warning("Nie udało się usunąć pliku %s z magazynu (obiekt został osierocony)", key)
