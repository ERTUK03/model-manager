from app.repositories.ml_model_repository import InMemoryMLModelRepository
from app.services.ml_model_service import MLModelService

_service = MLModelService(InMemoryMLModelRepository(seed=True))


def get_model_service() -> MLModelService:
    return _service
