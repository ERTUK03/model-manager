from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.ml_model_repository import SqlAlchemyMLModelRepository
from app.services.ml_model_service import MLModelService


def get_model_service(db: Session = Depends(get_db)) -> MLModelService:
    return MLModelService(SqlAlchemyMLModelRepository(db))
