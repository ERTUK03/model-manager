import logging
import time
import uuid

from fastapi import FastAPI, Request

logger = logging.getLogger("app.request")

# Sondy stanu są wywoływane co kilka sekund, więc nie zaśmiecają dziennika
SKIPPED_PREFIXES = ("/api/health",)
# Żądania, które nie pasują do żadnej trasy (np. skanery), grupujemy razem zamiast logować dowolne ścieżki
UNMATCHED = "nie-dopasowano"


def route_template(request: Request) -> str:
    """Ścieżka z nazwami parametrów zamiast wartości, np. /api/models/{model_id}.
    Pozwala grupować żądania do tej samej trasy niezależnie od identyfikatora."""
    if request.scope.get("route") is None:
        return UNMATCHED
    segments = request.url.path.split("/")
    for name, value in reversed(list(request.scope.get("path_params", {}).items())):
        for index in range(len(segments) - 1, -1, -1):
            if segments[index] == str(value):
                segments[index] = "{" + name + "}"
                break
    return "/".join(segments)


def register_request_logging(app: FastAPI) -> None:
    """Zapisuje jeden wpis na żądanie: metoda, ścieżka, kod odpowiedzi i czas w milisekundach.
    Nie loguje nagłówków (w tym tokenów), treści żądań ani parametrów zapytania."""

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:16]
        started = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            if not request.url.path.startswith(SKIPPED_PREFIXES):
                route = route_template(request)
                logger.info(
                    "request_completed",
                    extra={
                        "fields": {
                            "request_id": request_id,
                            "method": request.method,
                            "route": route,
                            "status": status,
                            "duration_ms": round((time.perf_counter() - started) * 1000, 1),
                        }
                    },
                )
