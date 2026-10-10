import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_model_service
from app.main import app
from app.repositories.ml_model_repository import InMemoryMLModelRepository
from app.services.ml_model_service import MLModelService


@pytest.fixture
def client():
    service = MLModelService(InMemoryMLModelRepository())
    app.dependency_overrides[get_model_service] = lambda: service
    # raise_server_exceptions=False: pozwala sprawdzić odpowiedź 500 zamiast przerywać test
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()
