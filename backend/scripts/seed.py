"""Wstawia przykładowe modele, jeśli tabela jest pusta.
Uruchomienie (z folderu backend):  python -m scripts.seed"""
from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models.ml_model import MLModel

SEED_MODELS = [
    {"name": "iris-classifier", "description": "Klasyfikacja gatunków irysów", "framework": "scikit-learn", "task": "Klasyfikacja", "version": "1.0.0", "accuracy": 0.967, "size_mb": 0.4, "status": "published"},
    {"name": "house-price-regressor", "description": "Predykcja cen mieszkań", "framework": "XGBoost", "task": "Regresja", "version": "2.1.0", "accuracy": 0.882, "size_mb": 12.3, "status": "published"},
    {"name": "sentiment-pl", "description": "Analiza sentymentu polskich opinii", "framework": "PyTorch", "task": "NLP", "version": "0.9.2", "accuracy": 0.911, "size_mb": 438.0, "status": "published"},
    {"name": "mnist-cnn", "description": "Rozpoznawanie cyfr pisanych ręcznie", "framework": "TensorFlow", "task": "Klasyfikacja obrazów", "version": "1.3.0", "accuracy": 0.992, "size_mb": 8.7, "status": "draft"},
    {"name": "churn-predictor", "description": "Przewidywanie odejść klientów", "framework": "ONNX", "task": "Klasyfikacja", "version": "1.0.1", "accuracy": 0.846, "size_mb": 3.1, "status": "archived"},
    {"name": "anomaly-detector", "description": "Wykrywanie anomalii w szeregach czasowych", "framework": "PyTorch", "task": "Wykrywanie anomalii", "version": "0.4.0", "accuracy": None, "size_mb": 21.5, "status": "draft"},
]


def main() -> None:
    with SessionLocal() as db:
        if db.scalar(select(func.count()).select_from(MLModel)):
            print("Tabela nie jest pusta, pomijam.")
            return
        db.add_all(MLModel(**item) for item in SEED_MODELS)
        db.commit()
        print(f"Dodano {len(SEED_MODELS)} modeli.")


if __name__ == "__main__":
    main()
