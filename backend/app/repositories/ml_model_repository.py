from datetime import datetime, timezone

SEED_MODELS = [
    {"name": "iris-classifier", "description": "Klasyfikacja gatunków irysów", "framework": "scikit-learn", "task": "Klasyfikacja", "version": "1.0.0", "accuracy": 0.967, "size_mb": 0.4, "status": "published"},
    {"name": "house-price-regressor", "description": "Predykcja cen mieszkań", "framework": "XGBoost", "task": "Regresja", "version": "2.1.0", "accuracy": 0.882, "size_mb": 12.3, "status": "published"},
    {"name": "sentiment-pl", "description": "Analiza sentymentu polskich opinii", "framework": "PyTorch", "task": "NLP", "version": "0.9.2", "accuracy": 0.911, "size_mb": 438.0, "status": "published"},
    {"name": "mnist-cnn", "description": "Rozpoznawanie cyfr pisanych ręcznie", "framework": "TensorFlow", "task": "Klasyfikacja obrazów", "version": "1.3.0", "accuracy": 0.992, "size_mb": 8.7, "status": "draft"},
    {"name": "churn-predictor", "description": "Przewidywanie odejść klientów", "framework": "ONNX", "task": "Klasyfikacja", "version": "1.0.1", "accuracy": 0.846, "size_mb": 3.1, "status": "archived"},
    {"name": "anomaly-detector", "description": "Wykrywanie anomalii w szeregach czasowych", "framework": "PyTorch", "task": "Wykrywanie anomalii", "version": "0.4.0", "accuracy": None, "size_mb": 21.5, "status": "draft"},
]


def _now() -> datetime:
    return datetime.now(timezone.utc)


class InMemoryMLModelRepository:
    """Tymczasowe przechowywanie w pamięci. Zostanie zastąpione przez bazę danych."""

    def __init__(self, seed: bool = False):
        self._items: dict[int, dict] = {}
        self._next_id = 1
        if seed:
            for item in SEED_MODELS:
                self.add(item)

    def list(self) -> list[dict]:
        return [dict(item) for item in self._items.values()]

    def get(self, model_id: int) -> dict | None:
        item = self._items.get(model_id)
        return dict(item) if item else None

    def add(self, data: dict) -> dict:
        now = _now()
        item = {**data, "id": self._next_id, "created_at": now, "updated_at": now}
        self._items[self._next_id] = item
        self._next_id += 1
        return dict(item)

    def update(self, model_id: int, data: dict) -> dict | None:
        item = self._items.get(model_id)
        if item is None:
            return None
        item.update(data)
        item["updated_at"] = _now()
        return dict(item)

    def delete(self, model_id: int) -> bool:
        return self._items.pop(model_id, None) is not None
