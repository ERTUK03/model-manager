import logging

from fastapi import FastAPI
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

# Sondy stanu wywoływane co kilka sekund nie powinny tworzyć śladów ani zwiększać kosztów
EXCLUDED_URLS = "api/health"


def instrument_fastapi(app: FastAPI, tracer_provider=None) -> None:
    """Każde żądanie HTTP dostaje ślad z czasem trwania i kodem odpowiedzi (tabela requests w Application Insights)."""
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=tracer_provider,
        excluded_urls=EXCLUDED_URLS,
        exclude_spans=["send", "receive"],  # bez wewnętrznych rozpiętości, które tylko powiększają dane
    )


def setup_telemetry(app: FastAPI, engine: Engine, connection_string: str | None) -> bool:
    """Włącza wysyłanie telemetrii do Application Insights, jeśli podano connection string.
    Telemetria nigdy nie może przeszkodzić w działaniu aplikacji: błąd konfiguracji jest tylko logowany."""
    if not connection_string:
        logger.info("Application Insights wyłączone (brak APPLICATIONINSIGHTS_CONNECTION_STRING)")
        return False
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

        configure_azure_monitor(connection_string=connection_string)
        instrument_fastapi(app)
        SQLAlchemyInstrumentor().instrument(engine=engine)  # zapytania do bazy jako zależności z czasem trwania
    except Exception:
        logger.exception("Nie udało się włączyć Application Insights, aplikacja działa bez telemetrii")
        return False
    logger.info("Application Insights włączone")
    return True
