from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import get_settings
from app.core.database import engine
from app.core.error_handlers import register_exception_handlers
from app.core.logging_config import configure_logging
from app.core.middleware import register_upload_limit
from app.core.request_logging import register_request_logging
from app.core.telemetry import setup_telemetry

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title="Model Manager API",
    version=settings.app_version,
    # Dokumentacja pod /api/..., żeby działała przez proxy nginx
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url=None,
)

if settings.cors_origins_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )

register_exception_handlers(app)
register_upload_limit(app)
register_request_logging(app)  # ostatni: obejmuje wszystkie pozostałe warstwy, także odrzucone żądania
app.include_router(api_router, prefix="/api")

# Telemetria (czas odpowiedzi, błędy, zapytania do bazy) trafia do Application Insights, jeśli podano connection string
setup_telemetry(
    app,
    engine,
    settings.applicationinsights_connection_string.get_secret_value()
    if settings.applicationinsights_connection_string
    else None,
)
