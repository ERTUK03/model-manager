class AppError(Exception):
    """Bazowy błąd aplikacji."""


class NotFoundError(AppError):
    def __init__(self, resource: str = "Zasób"):
        self.resource = resource
        super().__init__(f"{resource} nie istnieje")


class ConflictError(AppError):
    """Konflikt z aktualnym stanem danych (np. zajęty adres e-mail)."""


class UnauthorizedError(AppError):
    """Brak lub nieprawidłowe uwierzytelnienie."""


class ForbiddenError(AppError):
    """Użytkownik jest zalogowany, ale nie ma uprawnień do operacji."""


class BadRequestError(AppError):
    """Żądanie jest poprawne składniowo, ale nie spełnia reguł (np. zły typ pliku)."""


class PayloadTooLargeError(AppError):
    """Przesłane dane przekraczają dozwolony rozmiar."""


class StorageError(AppError):
    """Magazyn plików jest niedostępny lub odrzucił operację."""


class ServiceUnavailableError(AppError):
    """Funkcja nie jest skonfigurowana w tym środowisku."""
