from sqlalchemy.exc import OperationalError

from app.core.database import get_db
from app.main import app


def test_health_returns_status_and_version_without_authentication(anon_client):
    response = anon_client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "test-version"}


def test_ready_checks_database(anon_client):
    response = anon_client.get("/api/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "version": "test-version"}


def test_ready_returns_503_when_database_is_down(anon_client):
    class BrokenSession:
        def execute(self, *args, **kwargs):
            raise OperationalError("SELECT 1", {}, Exception("brak połączenia"))

    app.dependency_overrides[get_db] = lambda: BrokenSession()
    response = anon_client.get("/api/health/ready")
    assert response.status_code == 503
    assert response.json() == {"detail": "Baza danych jest niedostępna"}
    # zwykły /health nie zależy od bazy
    assert anon_client.get("/api/health").status_code == 200


def test_api_documentation_shows_version(anon_client):
    assert anon_client.get("/api/openapi.json").json()["info"]["version"] == "test-version"
