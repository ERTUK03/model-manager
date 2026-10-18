from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.ml_model import MLModel
from app.schemas.ml_model import MLModelListQuery


def escape_like(value: str) -> str:
    """Znaki % i _ wpisane przez użytkownika mają być traktowane dosłownie."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


class SqlAlchemyMLModelRepository:
    """Jedyne miejsce, które wykonuje zapytania do bazy danych."""

    def __init__(self, db: Session):
        self.db = db

    def list(self, params: MLModelListQuery) -> tuple[list[MLModel], int]:
        conditions = []
        if params.search:
            pattern = f"%{escape_like(params.search)}%"
            conditions.append(
                or_(
                    MLModel.name.ilike(pattern, escape="\\"),
                    MLModel.description.ilike(pattern, escape="\\"),
                )
            )
        if params.framework:
            conditions.append(MLModel.framework == params.framework)
        if params.status:
            conditions.append(MLModel.status == params.status)

        total = self.db.scalar(select(func.count()).select_from(MLModel).where(*conditions)) or 0

        column = getattr(MLModel, params.sort)
        ascending = params.order == "asc"
        primary = column.asc() if ascending else column.desc()
        # Puste wartości (np. brak dokładności) zawsze na końcu; id rozstrzyga remisy
        statement = (
            select(MLModel)
            .where(*conditions)
            .order_by(primary.nulls_last(), MLModel.id.asc() if ascending else MLModel.id.desc())
            .offset((params.page - 1) * params.page_size)
            .limit(params.page_size)
        )
        return list(self.db.scalars(statement)), total

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
