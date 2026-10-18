from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_history_service, require_admin
from app.schemas.history import HistoryListQuery, HistoryPage
from app.services.history_service import HistoryService

# Dziennik wszystkich zmian (także usunięć): tylko dla administratora
router = APIRouter(prefix="/history", tags=["history"], dependencies=[Depends(require_admin)])


@router.get("", response_model=HistoryPage)
def list_history(
    params: Annotated[HistoryListQuery, Query()],
    service: HistoryService = Depends(get_history_service),
):
    return service.list_page(params)
