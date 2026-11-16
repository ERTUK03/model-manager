import logging
import time

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.exceptions import ServiceUnavailableError

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


@router.get("/health")
def health_check():
    """Sprawdza, czy proces działa, i zwraca wersję. Nie dotyka bazy (nadaje się na sondę żywotności)."""
    return {"status": "ok", "version": get_settings().app_version}


@router.get("/health/ready")
def readiness_check(db: Session = Depends(get_db)):
    """Sprawdza połączenie z bazą danych i zwraca czas odpowiedzi bazy. Gdy baza nie odpowiada, zwraca 503."""
    started = time.perf_counter()
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        # Do dziennika trafia tylko typ błędu: komunikat sterownika mógłby zawierać dane połączenia
        logger.warning("Sprawdzenie gotowości: baza danych niedostępna (%s)", type(exc).__name__)
        raise ServiceUnavailableError("Baza danych jest niedostępna") from None
    latency_ms = round((time.perf_counter() - started) * 1000, 1)
    return {
        "status": "ready",
        "version": get_settings().app_version,
        "checks": {"database": {"status": "ok", "latency_ms": latency_ms}},
    }
