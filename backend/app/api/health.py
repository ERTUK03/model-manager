from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.exceptions import ServiceUnavailableError

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """Sprawdza, czy proces działa, i zwraca wersję. Nie dotyka bazy (nadaje się na sondę żywotności)."""
    return {"status": "ok", "version": get_settings().app_version}


@router.get("/health/ready")
def readiness_check(db: Session = Depends(get_db)):
    """Sprawdza także połączenie z bazą danych. Gdy baza nie odpowiada, zwraca 503."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise ServiceUnavailableError("Baza danych jest niedostępna") from None
    return {"status": "ready", "version": get_settings().app_version}
