import os

# Testy ZAWSZE używają osobnej, lokalnej bazy SQLite. Ustawienie przed importem aplikacji
# chroni prawdziwą bazę (z pliku .env) przed przypadkowym wyczyszczeniem.
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import app.models  # noqa: E402,F401  (rejestruje tabele w metadanych)
from app.core.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    # raise_server_exceptions=False: pozwala sprawdzić odpowiedź 500 zamiast przerywać test
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
