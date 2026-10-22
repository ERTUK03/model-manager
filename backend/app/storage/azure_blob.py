import logging
from datetime import datetime, timedelta, timezone
from typing import BinaryIO
from urllib.parse import quote

from azure.core.exceptions import AzureError, ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import BlobSasPermissions, BlobServiceClient, ContentSettings, generate_blob_sas

from app.core.exceptions import StorageError

logger = logging.getLogger(__name__)


def content_disposition(filename: str) -> str:
    """Nagłówek wymuszający pobranie pliku pod oryginalną nazwą (także z polskimi znakami)."""
    ascii_name = "".join(c if 32 <= ord(c) < 127 and c not in '"\\;' else "_" for c in filename) or "model"
    return f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{quote(filename, safe='')}"


class AzureBlobStorage:
    """Pliki modeli w Azure Blob Storage.

    Dwa tryby uwierzytelniania:
    - connection string (Azurite lub konto z kluczem): podpis SAS kluczem konta,
    - account_url + tożsamość zarządzana (Azure): podpis SAS kluczem delegowanym użytkownika, bez kluczy w aplikacji.
    """

    def __init__(self, container: str, connection_string: str | None = None, account_url: str | None = None):
        if connection_string:
            self.service = BlobServiceClient.from_connection_string(connection_string)
            self._account_key = self.service.credential.account_key
        else:
            from azure.identity import DefaultAzureCredential

            self.service = BlobServiceClient(account_url, credential=DefaultAzureCredential())
            self._account_key = None
        self.container = self.service.get_container_client(container)
        self._container_ready = False

    def _ensure_container(self) -> None:
        if self._container_ready:
            return
        try:
            self.container.create_container()
        except ResourceExistsError:
            pass
        self._container_ready = True

    def upload(self, key: str, fileobj: BinaryIO) -> None:
        try:
            self._ensure_container()
            self.container.upload_blob(
                key,
                fileobj,
                overwrite=True,
                content_settings=ContentSettings(content_type="application/octet-stream"),
            )
        except AzureError as exc:
            logger.exception("Błąd zapisu w magazynie plików")
            raise StorageError("Nie udało się zapisać pliku w magazynie. Spróbuj ponownie.") from exc

    def delete(self, key: str) -> None:
        try:
            self.container.delete_blob(key)
        except ResourceNotFoundError:
            pass
        except AzureError as exc:
            logger.exception("Błąd usuwania z magazynu plików")
            raise StorageError("Nie udało się usunąć pliku z magazynu.") from exc

    def download_url(self, key: str, filename: str, expires_in: int) -> str:
        """Krótko ważny adres tylko do odczytu jednego obiektu (podpis SAS)."""
        try:
            now = datetime.now(timezone.utc)
            expiry = now + timedelta(seconds=expires_in)
            options = {
                "account_name": self.service.account_name,
                "container_name": self.container.container_name,
                "blob_name": key,
                "permission": BlobSasPermissions(read=True),
                "expiry": expiry,
                "content_disposition": content_disposition(filename),
            }
            if self._account_key:
                token = generate_blob_sas(account_key=self._account_key, **options)
            else:
                delegation_key = self.service.get_user_delegation_key(now - timedelta(minutes=1), expiry)
                token = generate_blob_sas(user_delegation_key=delegation_key, **options)
            return f"{self.container.get_blob_client(key).url}?{token}"
        except AzureError as exc:
            logger.exception("Błąd generowania adresu pobierania")
            raise StorageError("Nie udało się przygotować pobierania pliku.") from exc
