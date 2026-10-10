from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ml_model import MLModel


class SqlAlchemyMLModelRepository:
    """Jedyne miejsce, które wykonuje zapytania do bazy danych."""

    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[MLModel]:
        return list(self.db.scalars(select(MLModel).order_by(MLModel.id)))

    def get(self, model_id: int) -> MLModel | None:
        return self.db.get(MLModel, model_id)

    def add(self, data: dict) -> MLModel:
        model = MLModel(**data)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def update(self, model_id: int, data: dict) -> MLModel | None:
        model = self.db.get(MLModel, model_id)
        if model is None:
            return None
        for key, value in data.items():
            setattr(model, key, value)
        self.db.commit()
        self.db.refresh(model)
        return model

    def delete(self, model_id: int) -> bool:
        model = self.db.get(MLModel, model_id)
        if model is None:
            return False
        self.db.delete(model)
        self.db.commit()
        return True
