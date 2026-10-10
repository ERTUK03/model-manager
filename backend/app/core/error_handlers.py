import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import NotFoundError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        errors = [
            {
                "field": ".".join(str(part) for part in err["loc"]),
                "message": err["msg"],
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=400,
            content={"detail": "Nieprawidłowe dane wejściowe", "errors": errors},
        )

    @app.exception_handler(Exception)
    async def unexpected_handler(request: Request, exc: Exception):
        # Szczegóły trafiają tylko do logów, nigdy do odpowiedzi
        logger.exception("Nieobsłużony błąd: %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"detail": "Wewnętrzny błąd serwera"})
