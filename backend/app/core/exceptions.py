class AppError(Exception):
    """Bazowy błąd aplikacji."""


class NotFoundError(AppError):
    def __init__(self, resource: str = "Zasób"):
        self.resource = resource
        super().__init__(f"{resource} nie istnieje")
