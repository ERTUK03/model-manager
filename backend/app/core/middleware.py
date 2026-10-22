import re

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import get_settings

UPLOAD_PATH = re.compile(r"^/api/models/\d+/file$")
MULTIPART_OVERHEAD = 64 * 1024  # zapas na nagłówki formularza


def register_upload_limit(app: FastAPI) -> None:
    """Odrzuca zbyt duże przesyłanie plików zanim serwer zacznie je odbierać (na podstawie Content-Length)."""

    @app.middleware("http")
    async def limit_upload_size(request: Request, call_next):
        if request.method == "POST" and UPLOAD_PATH.match(request.url.path):
            max_bytes = get_settings().max_upload_mb * 1024 * 1024
            length = request.headers.get("content-length", "")
            if length.isdigit() and int(length) > max_bytes + MULTIPART_OVERHEAD:
                return JSONResponse(
                    status_code=413,
                    content={"detail": f"Plik jest za duży (maksymalnie {get_settings().max_upload_mb} MB)"},
                )
        return await call_next(request)
