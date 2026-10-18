from math import ceil

from app.core.exceptions import NotFoundError
from app.models.user import User
from app.schemas.ml_model import MLModelCreate, MLModelListQuery, MLModelUpdate

# Pola, których zmiany trafiają do historii
TRACKED_FIELDS = ("name", "description", "framework", "task", "version", "accuracy", "size_mb", "status")


def _snapshot(model) -> dict:
    return {field: getattr(model, field) for field in TRACKED_FIELDS}


class MLModelService:
    """Logika biznesowa dla modeli ML. Nie zna HTTP ani szczegółów bazy danych."""

    def __init__(self, repository, history):
        self.repository = repository
        self.history = history

    def list_models(self, params: MLModelListQuery) -> dict:
        items, total = self.repository.list(params)
        return {
            "items": items,
            "total": total,
            "page": params.page,
            "page_size": params.page_size,
            "pages": ceil(total / params.page_size),
        }

    def get_model(self, model_id: int):
        model = self.repository.get(model_id)
        if model is None:
            raise NotFoundError("Model")
        return model

    def create_model(self, data: MLModelCreate, actor: User):
        model = self.repository.add(data.model_dump())
        changes = {field: {"from": None, "to": value} for field, value in _snapshot(model).items() if value is not None}
        self.history.add(model.id, model.name, "created", changes, actor)
        self.repository.commit()  # model i wpis w historii zapisują się razem albo wcale
        return model

    def update_model(self, model_id: int, data: MLModelUpdate, actor: User):
        model = self.get_model(model_id)
        before = _snapshot(model)
        new_values = data.model_dump()
        changes = {
            field: {"from": before[field], "to": new_values[field]}
            for field in TRACKED_FIELDS
            if before[field] != new_values[field]
        }
        if not changes:
            return model  # nic się nie zmieniło: nie tworzymy wpisu w historii
        updated = self.repository.update(model_id, new_values)
        self.history.add(model_id, updated.name, "updated", changes, actor)
        self.repository.commit()
        return updated

    def delete_model(self, model_id: int, actor: User) -> None:
        model = self.get_model(model_id)
        name = model.name
        self.repository.delete(model_id)
        self.history.add(model_id, name, "deleted", None, actor)
        self.repository.commit()
