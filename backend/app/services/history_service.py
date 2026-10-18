from math import ceil

from app.core.exceptions import NotFoundError
from app.schemas.history import HistoryListQuery


class HistoryService:
    def __init__(self, history, models):
        self.history = history
        self.models = models

    def list_for_model(self, model_id: int):
        entries = self.history.list_for_model(model_id)
        # Usunięty model nadal ma historię. 404 tylko dla identyfikatora, który nigdy nie istniał
        if not entries and self.models.get(model_id) is None:
            raise NotFoundError("Model")
        return entries

    def list_page(self, params: HistoryListQuery) -> dict:
        items, total = self.history.list_page(params)
        return {
            "items": items,
            "total": total,
            "page": params.page,
            "page_size": params.page_size,
            "pages": ceil(total / params.page_size),
        }
