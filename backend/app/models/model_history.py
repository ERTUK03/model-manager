from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ModelHistory(Base):
    """Dziennik zmian modeli. Wpisy zostają także po usunięciu modelu (stąd brak klucza obcego do ml_models)."""

    __tablename__ = "model_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)  # created | updated | deleted
    changes: Mapped[dict | None] = mapped_column(JSON)  # {pole: {"from": ..., "to": ...}}
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    user_email: Mapped[str | None] = mapped_column(String(254))  # kopia adresu: wpis zostaje czytelny po usunięciu konta
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
