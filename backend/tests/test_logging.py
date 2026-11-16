import json
import logging

from app.api.deps import get_model_service
from app.core.logging_config import JsonFormatter, configure_logging
from app.main import app


def request_records(caplog):
    return [r for r in caplog.records if r.name == "app.request" and r.getMessage() == "request_completed"]


def test_request_is_logged_with_status_route_and_duration(client, caplog):
    caplog.set_level(logging.INFO, logger="app.request")
    assert client.get("/api/models").status_code == 200
    (record,) = request_records(caplog)
    fields = record.fields
    assert fields["method"] == "GET"
    assert fields["route"] == "/api/models"
    assert fields["status"] == 200
    assert fields["duration_ms"] >= 0
    assert fields["request_id"]


def test_route_template_groups_requests_with_different_ids(client, caplog):
    caplog.set_level(logging.INFO, logger="app.request")
    client.get("/api/models/1")
    client.get("/api/models/2")
    assert {r.fields["route"] for r in request_records(caplog)} == {"/api/models/{model_id}"}


def test_requests_matching_no_route_are_grouped(anon_client, caplog):
    caplog.set_level(logging.INFO, logger="app.request")
    assert anon_client.get("/api/wp-admin/setup.php").status_code == 404
    assert request_records(caplog)[-1].fields["route"] == "nie-dopasowano"  # bez dowolnych ścieżek od skanerów


def test_failed_requests_are_logged_with_their_status(client, caplog):
    caplog.set_level(logging.INFO, logger="app.request")
    client.get("/api/models/999")
    assert request_records(caplog)[-1].fields["status"] == 404

    class Broken:
        def list_models(self, *args, **kwargs):
            raise RuntimeError("boom")

    app.dependency_overrides[get_model_service] = lambda: Broken()
    client.get("/api/models")
    assert request_records(caplog)[-1].fields["status"] == 500


def test_health_probes_are_not_logged(anon_client, caplog):
    caplog.set_level(logging.INFO, logger="app.request")
    anon_client.get("/api/health")
    anon_client.get("/api/health/ready")
    assert request_records(caplog) == []


def test_request_log_contains_no_secrets(client, caplog):
    caplog.set_level(logging.INFO, logger="app.request")
    token = client.headers["Authorization"]
    client.get("/api/models?search=tajne-haslo")
    dump = json.dumps([r.fields for r in request_records(caplog)])
    assert token.split()[-1] not in dump
    assert "tajne-haslo" not in dump  # parametry zapytania nie trafiają do dziennika


def test_request_id_is_returned_and_can_be_supplied(anon_client):
    generated = anon_client.get("/api/health").headers["x-request-id"]
    assert len(generated) >= 8
    supplied = anon_client.get("/api/health", headers={"X-Request-ID": "moj-identyfikator"})
    assert supplied.headers["x-request-id"] == "moj-identyfikator"


def test_json_formatter_produces_valid_json_with_fields():
    record = logging.LogRecord("app.request", logging.INFO, __file__, 1, "request_completed", None, None)
    record.fields = {"status": 200, "duration_ms": 12.5}
    parsed = json.loads(JsonFormatter().format(record))
    assert parsed["message"] == "request_completed"
    assert parsed["level"] == "INFO"
    assert parsed["status"] == 200 and parsed["duration_ms"] == 12.5
    assert parsed["time"].endswith("+00:00")


def test_json_formatter_includes_exceptions():
    try:
        raise ValueError("awaria")
    except ValueError:
        import sys

        record = logging.LogRecord("x", logging.ERROR, __file__, 1, "błąd", None, sys.exc_info())
    assert "ValueError: awaria" in json.loads(JsonFormatter().format(record))["exception"]


def test_configure_logging_is_idempotent():
    configure_logging("INFO")
    configure_logging("INFO")
    assert len(logging.getLogger().handlers) == 1
