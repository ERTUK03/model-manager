# Dokumentacja API

Wszystkie ścieżki mają prefiks `/api`. Interaktywna dokumentacja (Swagger UI) jest dostępna pod `/api/docs`, a specyfikacja OpenAPI pod `/api/openapi.json`. Format danych: JSON (UTF-8).

> Autoryzacja (JWT) i role jeszcze nie są zaimplementowane. Po ich dodaniu endpointy zapisu będą wymagały tokenu.

## Endpointy

| Metoda | Ścieżka | Opis | Kody sukcesu |
|---|---|---|---|
| `GET` | `/api/health` | Sprawdzenie, czy API działa | 200 |
| `GET` | `/api/models` | Lista modeli | 200 |
| `GET` | `/api/models/{id}` | Szczegóły modelu | 200 |
| `POST` | `/api/models` | Utworzenie modelu | 201 |
| `PUT` | `/api/models/{id}` | Pełna aktualizacja modelu | 200 |
| `DELETE` | `/api/models/{id}` | Usunięcie modelu | 204 (bez treści) |

## Zasób `Model`

| Pole | Typ | Wymagane | Reguły |
|---|---|---|---|
| `id` | liczba całkowita | tylko odczyt | nadawane przez bazę, ≥ 1 |
| `name` | tekst | tak | 2–100 znaków, spacje na brzegach są usuwane |
| `description` | tekst | nie | do 500 znaków |
| `framework` | tekst | tak | jedna z wartości: `scikit-learn`, `XGBoost`, `PyTorch`, `TensorFlow`, `ONNX`, `Other` |
| `task` | tekst | tak | 2–50 znaków |
| `version` | tekst | tak | format `X.Y.Z`, np. `1.0.0` |
| `accuracy` | liczba | nie | od 0 do 1 |
| `size_mb` | liczba | nie | ≥ 0 |
| `status` | tekst | nie (domyślnie `draft`) | `draft`, `published` lub `archived` |
| `created_at` | data i czas (ISO 8601) | tylko odczyt | ustawiane przez serwer |
| `updated_at` | data i czas (ISO 8601) | tylko odczyt | aktualizowane przez serwer |

Nieznane pola w żądaniu są odrzucane (kod 400). Reguły walidacji są takie same po stronie klienta (`frontend/src/validation/modelSchema.js`) i serwera (`backend/app/schemas/ml_model.py`).

## Przykłady

### Utworzenie modelu

```http
POST /api/models
Content-Type: application/json

{
  "name": "iris-classifier",
  "description": "Klasyfikacja gatunków irysów",
  "framework": "scikit-learn",
  "task": "Klasyfikacja",
  "version": "1.0.0",
  "accuracy": 0.967,
  "size_mb": 0.4,
  "status": "draft"
}
```

Odpowiedź `201 Created`:

```json
{
  "id": 1,
  "name": "iris-classifier",
  "description": "Klasyfikacja gatunków irysów",
  "framework": "scikit-learn",
  "task": "Klasyfikacja",
  "version": "1.0.0",
  "accuracy": 0.967,
  "size_mb": 0.4,
  "status": "draft",
  "created_at": "2026-10-10T12:00:00Z",
  "updated_at": "2026-10-10T12:00:00Z"
}
```

### Przykład w curl

```bash
curl -X POST http://localhost:8000/api/models \
  -H "Content-Type: application/json" \
  -d '{"name":"iris","framework":"ONNX","task":"Klasyfikacja","version":"1.0.0"}'

curl http://localhost:8000/api/models
curl -X DELETE http://localhost:8000/api/models/1
```

## Format błędów

Błąd walidacji (400):

```json
{
  "detail": "Nieprawidłowe dane wejściowe",
  "errors": [
    { "field": "body.version", "message": "String should match pattern '^\\d+\\.\\d+\\.\\d+$'" }
  ]
}
```

Pozostałe błędy mają postać `{ "detail": "..." }`.

| Kod | Znaczenie | Przykład |
|---|---|---|
| 200 | OK | pobranie listy lub szczegółów, aktualizacja |
| 201 | Utworzono | poprawny `POST /api/models` |
| 204 | Brak treści | poprawne usunięcie |
| 400 | Nieprawidłowe dane | błędny format wersji, dokładność spoza zakresu, nieznane pole, identyfikator niebędący liczbą |
| 404 | Nie znaleziono | model o podanym `id` nie istnieje |
| 500 | Błąd serwera | nieoczekiwany wyjątek; odpowiedź zawiera ogólny komunikat, szczegóły są tylko w logach |

Uwaga: FastAPI domyślnie zwraca 422 dla błędów walidacji. W tym projekcie są one zamieniane na 400 (`backend/app/core/error_handlers.py`).
