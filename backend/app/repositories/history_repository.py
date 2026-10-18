from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.model_history import ModelHistory
from app.models.user import User
from app.schemas.history import HistoryListQuery


class HistoryRepository:
    """Zapytania o dziennik zmian. Zapis nie wykonuje commitu: robi go serwis razem ze zmianą modelu."""

    def __init__(self, db: Session):
        self.db = db

    def add(self, model_id: int, model_name: str, action: str, changes: dict | None, actor: User) -> ModelHistory:
        entry = ModelHistory(
            model_id=model_id,
            model_name=model_name,
            action=action,
            changes=changes,
            user_id=actor.id,
            user_email=actor.email,
        )
        self.db.add(entry)
        self.db.flush()
        return entry

    def list_for_model(self, model_id: int) -> list[ModelHistory]:
        statement = select(ModelHistory).where(ModelHistory.model_id == model_id).order_by(ModelHistory.id.desc())
        return list(self.db.scalars(statement))

    def list_page(self, params: HistoryListQuery) -> tuple[list[ModelHistory], int]:
        conditions = []
        if params.action:
            conditions.append(ModelHistory.action == params.action)
        if params.model_id:
            conditions.append(ModelHistory.model_id == params.model_id)
        total = self.db.scalar(select(func.count()).select_from(ModelHistory).where(*conditions)) or 0
        statement = (
            select(ModelHistory)
            .where(*conditions)
            .order_by(ModelHistory.id.desc())
            .offset((params.page - 1) * params.page_size)
            .limit(params.page_size)
        )
        return list(self.db.scalars(statement)), total
