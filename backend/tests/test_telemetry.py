import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from app.core.database import engine
from app.core.telemetry import instrument_fastapi, setup_telemetry
from app.main import app as main_app


def build_app():
    app = FastAPI()

    @app.get("/api/models")
    def models():
        return []

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app


@pytest.fixture
def exporter():
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    app = build_app()
    instrument_fastapi(app, tracer_provider=provider)
    yield exporter, TestClient(app)
    FastAPIInstrumentor.uninstrument_app(app)


def test_each_request_produces_a_span_with_duration_and_status(exporter):
    spans, client = exporter
    assert client.get("/api/models").status_code == 200
    (span,) = spans.get_finished_spans()
    assert span.name == "GET /api/models"
    assert span.attributes["http.status_code"] == 200
    assert span.end_time > span.start_time


def test_health_probes_and_internal_asgi_spans_are_not_recorded(exporter):
    spans, client = exporter
    client.get("/api/health")
    client.get("/api/models")
    assert [s.name for s in spans.get_finished_spans()] == ["GET /api/models"]


def test_telemetry_is_disabled_without_connection_string():
    assert setup_telemetry(main_app, engine, None) is False
    assert setup_telemetry(main_app, engine, "") is False


def test_configuration_errors_never_break_the_application(monkeypatch, caplog):
    def broken(*args, **kwargs):
        raise RuntimeError("zły connection string")

    monkeypatch.setattr("azure.monitor.opentelemetry.configure_azure_monitor", broken)
    assert setup_telemetry(main_app, engine, "InstrumentationKey=x") is False
    assert "Nie udało się włączyć Application Insights" in caplog.text


def test_successful_setup_instruments_the_application(monkeypatch):
    calls = []
    monkeypatch.setattr("azure.monitor.opentelemetry.configure_azure_monitor", lambda **kwargs: calls.append(kwargs))
    app = build_app()
    try:
        assert setup_telemetry(app, engine, "InstrumentationKey=00000000-0000-0000-0000-000000000000") is True
        assert calls == [{"connection_string": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}]
        assert getattr(app, "_is_instrumented_by_opentelemetry", False)
    finally:
        FastAPIInstrumentor.uninstrument_app(app)
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

        SQLAlchemyInstrumentor().uninstrument()
