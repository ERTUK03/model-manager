from app.core.exceptions import NotFoundError
from app.schemas.ml_model import MLModelCreate, MLModelUpdate


class MLModelService:
    """Logika biznesowa dla modeli ML. Nie zna HTTP ani szczegółów bazy danych."""

    def __init__(self, repository):
        self.repository = repository

    def list_models(self):
        return self.repository.list()

    def get_model(self, model_id: int):
        model = self.repository.get(model_id)
        if model is None:
            raise NotFoundError("Model")
        return model

    def create_model(self, data: MLModelCreate):
        return self.repository.add(data.model_dump())

    def update_model(self, model_id: int, data: MLModelUpdate):
        model = self.repository.update(model_id, data.model_dump())
        if model is None:
            raise NotFoundError("Model")
        return model

    def delete_model(self, model_id: int) -> None:
        if not self.repository.delete(model_id):
            raise NotFoundError("Model")
