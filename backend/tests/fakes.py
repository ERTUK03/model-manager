from app.core.exceptions import StorageError


class FakeStorage:
    """Magazyn plików w pamięci, do testów."""

    def __init__(self):
        self.files: dict[str, bytes] = {}
        self.fail_upload = False

    def upload(self, key, fileobj):
        if self.fail_upload:
            raise StorageError("Nie udało się zapisać pliku w magazynie. Spróbuj ponownie.")
        self.files[key] = fileobj.read()

    def delete(self, key):
        self.files.pop(key, None)

    def download_url(self, key, filename, expires_in):
        return f"https://storage.test/{key}?sig=fake&ttl={expires_in}"
