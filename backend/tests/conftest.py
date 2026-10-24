import os

# Testy ZAWSZE używają osobnej, lokalnej bazy SQLite. Ustawienie przed importem aplikacji
# chroni prawdziwą bazę (z pliku .env) przed przypadkowym wyczyszczeniem.
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
# Wartość wyłącznie testowa, nieużywana nigdzie poza testami
os.environ["JWT_SECRET"] = "test-only-secret-not-for-production-use"
# Limit przesyłania ustawiony nisko, żeby testy mogły sprawdzić odrzucanie zbyt dużych plików
os.environ["MAX_UPLOAD_MB"] = "1"
os.environ["STORAGE_CONNECTION_STRING"] = ""
os.environ["STORAGE_ACCOUNT_URL"] = ""
os.environ["STORAGE_CONTAINER"] = "models"
os.environ["DOWNLOAD_URL_EXPIRE_SECONDS"] = "300"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import app.models  # noqa: E402,F401  (rejestruje tabele w metadanych)
from app.api.deps import get_file_storage, get_storage_or_none  # noqa: E402
from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.core.roles import ROLE_ADMIN, ROLE_USER  # noqa: E402
from app.core.security import create_access_token, hash_password  # noqa: E402
from app.main import app  # noqa: E402
from app.repositories.user_repository import UserRepository  # noqa: E402
from tests.fakes import FakeStorage  # noqa: E402


def _create_user(email: str, role: str) -> dict:
    """Tworzy użytkownika w bazie i zwraca nagłówek z jego tokenem."""
    with SessionLocal() as db:
        user = UserRepository(db).add(email, hash_password("Haslo1234"), role)
        return {"Authorization": f"Bearer {create_access_token(user.id)}"}


@pytest.fixture(autouse=True)
def database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def anon_client():
    """Klient bez tokenu."""
    # raise_server_exceptions=False: pozwala sprawdzić odpowiedź 500 zamiast przerywać test
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture
def client():
    """Klient zalogowany jako administrator (domyślny w testach CRUD)."""
    headers = _create_user("admin@example.com", ROLE_ADMIN)
    with TestClient(app, raise_server_exceptions=False, headers=headers) as test_client:
        yield test_client


@pytest.fixture
def user_client():
    """Klient zalogowany jako zwykły użytkownik."""
    headers = _create_user("user@example.com", ROLE_USER)
    with TestClient(app, raise_server_exceptions=False, headers=headers) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def storage():
    """Atrapa magazynu plików: testy nie łączą się z Azure ani z emulatorem."""
    fake = FakeStorage()
    app.dependency_overrides[get_file_storage] = lambda: fake
    app.dependency_overrides[get_storage_or_none] = lambda: fake
    yield fake
