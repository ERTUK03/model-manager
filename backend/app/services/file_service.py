import hashlib
import uuid
from pathlib import PurePosixPath
from typing import BinaryIO

from app.core.exceptions import BadRequestError, NotFoundError, PayloadTooLargeError
from app.models.user import User
from app.storage.base import FileStorage, delete_quietly

ALLOWED_EXTENSIONS = (".pkl", ".joblib", ".onnx", ".pt", ".pth", ".h5", ".safetensors")
CHUNK_SIZE = 1024 * 1024
MEGABYTE = 1024 * 1024


def sanitize_filename(filename: str | None) -> str:
    """Zostawia samą nazwę pliku: bez ścieżki, znaków sterujących i kropek na początku."""
    name = (filename or "").replace("\\", "/").rsplit("/", 1)[-1]
    name = "".join(ch for ch in name if ch.isprintable()).strip().lstrip(".")
    return name[:255]


def measure(fileobj: BinaryIO) -> tuple[int, str]:
    """Rozmiar i suma SHA-256, liczone porcjami (plik nie jest wczytywany do pamięci w całości)."""
    fileobj.seek(0)
    digest = hashlib.sha256()
    size = 0
    while chunk := fileobj.read(CHUNK_SIZE):
        size += len(chunk)
        digest.update(chunk)
    fileobj.seek(0)
    return size, digest.hexdigest()


class FileService:
    """Pliki modeli: zapis w magazynie powiązany z rekordem w bazie i wpisem w historii."""

    def __init__(self, models, history, storage: FileStorage, max_upload_mb: int, download_expires_in: int = 300):
        self.models = models
        self.history = history
        self.storage = storage
        self.max_upload_mb = max_upload_mb
        self.download_expires_in = download_expires_in

    def _get_model(self, model_id: int):
        model = self.models.get(model_id)
        if model is None:
            raise NotFoundError("Model")
        return model

    def upload(self, model_id: int, filename: str | None, fileobj: BinaryIO, actor: User):
        model = self._get_model(model_id)

        name = sanitize_filename(filename)
        if not name:
            raise BadRequestError("Brak nazwy pliku")
        extension = PurePosixPath(name).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise BadRequestError(f"Niedozwolony typ pliku. Dozwolone rozszerzenia: {', '.join(ALLOWED_EXTENSIONS)}")

        size, sha256 = measure(fileobj)
        if size == 0:
            raise BadRequestError("Plik jest pusty")
        if size > self.max_upload_mb * MEGABYTE:
            raise PayloadTooLargeError(f"Plik jest za duży (maksymalnie {self.max_upload_mb} MB)")

        old_key, old_name, old_size_mb = model.file_key, model.file_name, model.size_mb
        new_key = f"models/{model_id}/{uuid.uuid4().hex}{extension}"
        new_size_mb = round(size / MEGABYTE, 3)

        self.storage.upload(new_key, fileobj)
        try:
            updated = self.models.update(
                model_id,
                {
                    "file_key": new_key,
                    "file_name": name,
                    "file_size": size,
                    "file_sha256": sha256,
                    "size_mb": new_size_mb,  # rozmiar pochodzi teraz z pliku
                },
            )
            changes = {"file_name": {"from": old_name, "to": name}}
            if old_size_mb != new_size_mb:
                changes["size_mb"] = {"from": old_size_mb, "to": new_size_mb}
            self.history.add(model_id, updated.name, "updated", changes, actor)
            self.models.commit()
        except Exception:
            delete_quietly(self.storage, new_key)  # baza się nie zapisała: nie zostawiamy osieroconego pliku
            raise

        if old_key:
            delete_quietly(self.storage, old_key)
        return updated

    def remove(self, model_id: int, actor: User):
        model = self._get_model(model_id)
        if not model.file_key:
            raise NotFoundError("Plik")
        old_key, old_name = model.file_key, model.file_name

        updated = self.models.update(
            model_id, {"file_key": None, "file_name": None, "file_size": None, "file_sha256": None}
        )
        self.history.add(model_id, updated.name, "updated", {"file_name": {"from": old_name, "to": None}}, actor)
        self.models.commit()
        delete_quietly(self.storage, old_key)
        return updated

    def download_info(self, model_id: int) -> dict:
        model = self._get_model(model_id)
        if not model.file_key:
            raise NotFoundError("Plik")
        return {
            "url": self.storage.download_url(model.file_key, model.file_name, self.download_expires_in),
            "file_name": model.file_name,
            "file_size": model.file_size,
            "expires_in": self.download_expires_in,
        }
