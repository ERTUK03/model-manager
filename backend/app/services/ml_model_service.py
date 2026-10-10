from app.schemas.ml_model import MLModelCreate, MLModelUpdate


class MLModelService:
    """Logika biznesowa dla modeli ML. Nie zna HTTP ani szczegółów bazy danych."""

    def __init__(self, repository):
        self.repository = repository

    def list_models(self):
        return self.repository.list()

    def get_model(self, model_id: int):
        return self.repository.get(model_id)

    def create_model(self, data: MLModelCreate):
        return self.repository.add(data.model_dump())

    def update_model(self, model_id: int, data: MLModelUpdate):
        return self.repository.update(model_id, data.model_dump())

    def delete_model(self, model_id: int) -> bool:
        return self.repository.delete(model_id)
