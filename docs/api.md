# Dokumentacja API

Wszystkie ścieżki mają prefiks `/api`. Interaktywna dokumentacja (Swagger UI) jest dostępna pod `/api/docs`, a specyfikacja OpenAPI pod `/api/openapi.json`. Format danych: JSON (UTF-8).

## Uwierzytelnianie

Endpointy chronione wymagają tokenu JWT w nagłówku:

```
Authorization: Bearer <access_token>
```

Token uzyskasz przez `POST /api/auth/login`. W Swaggerze użyj przycisku **Authorize** i wklej sam token (bez słowa `Bearer`). Token jest ważny domyślnie 60 minut (`JWT_EXPIRE_MINUTES`).

## Endpointy

| Metoda | Ścieżka | Opis | Dostęp | Kody sukcesu |
|---|---|---|---|---|
| `GET` | `/api/health` | Sprawdzenie, czy API działa | publiczny | 200 |
| `POST` | `/api/auth/register` | Rejestracja konta z rolą `user` | publiczny | 201 |
| `POST` | `/api/auth/login` | Logowanie, zwraca token | publiczny | 200 |
| `GET` | `/api/auth/me` | Dane zalogowanego użytkownika | zalogowany | 200 |
| `GET` | `/api/models` | Lista modeli: wyszukiwanie, filtry, sortowanie, paginacja | zalogowany | 200 |
| `GET` | `/api/models/{id}` | Szczegóły modelu | zalogowany | 200 |
| `GET` | `/api/models/{id}/history` | Historia zmian modelu | zalogowany | 200 |
| `GET` | `/api/models/{id}/download` | Krótko ważny adres do pobrania pliku | zalogowany | 200 |
| `POST` | `/api/models/{id}/file` | Dodanie lub zastąpienie pliku modelu | administrator | 200 |
| `DELETE` | `/api/models/{id}/file` | Usunięcie pliku modelu | administrator | 200 |
| `POST` | `/api/models` | Utworzenie modelu | administrator | 201 |
| `PUT` | `/api/models/{id}` | Pełna aktualizacja modelu | administrator | 200 |
| `DELETE` | `/api/models/{id}` | Usunięcie modelu | administrator | 204 (bez treści) |
| `GET` | `/api/history` | Dziennik zmian wszystkich modeli | administrator | 200 |

## Użytkownicy

### Rejestracja

`POST /api/auth/register`

```json
{ "email": "jan@example.com", "password": "Haslo1234" }
```

| Pole | Reguły |
|---|---|
| `email` | poprawny adres e-mail; spacje na brzegach są usuwane, a wielkość liter ignorowana (adres zapisywany małymi literami) |
| `password` | 8–128 znaków, co najmniej jedna litera i jedna cyfra |

Nieznane pola (np. `role`) są odrzucane kodem 400, więc rolę `admin` nie da się nadać przez rejestrację. Odpowiedź `201 Created`:

```json
{ "id": 2, "email": "jan@example.com", "role": "user", "created_at": "2026-10-10T12:00:00Z" }
```

Hasło nie jest nigdy zwracane. W bazie przechowywany jest wyłącznie hash (Argon2id).

### Logowanie

`POST /api/auth/login` z ciałem `{ "email": "...", "password": "..." }`. Odpowiedź `200 OK`:

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": { "id": 2, "email": "jan@example.com", "role": "user", "created_at": "2026-10-10T12:00:00Z" }
}
```

Błędny e-mail i błędne hasło dają tę samą odpowiedź `401` z komunikatem „Nieprawidłowy e-mail lub hasło”, żeby nie ujawniać, które adresy mają konta.

## Lista modeli

`GET /api/models` zwraca jedną stronę wyników. Wszystkie parametry są opcjonalne:

| Parametr | Domyślnie | Opis |
|---|---|---|
| `search` | brak | Fragment nazwy lub opisu, wielkość liter nie ma znaczenia (maks. 100 znaków) |
| `framework` | brak | Filtr: `scikit-learn`, `XGBoost`, `PyTorch`, `TensorFlow`, `ONNX` lub `Other` |
| `status` | brak | Filtr: `draft`, `published` lub `archived` |
| `sort` | `created_at` | Pole sortowania: `created_at`, `updated_at`, `name`, `accuracy`, `size_mb` |
| `order` | `desc` | Kierunek: `asc` lub `desc`. Modele bez wartości w polu sortowania są zawsze na końcu |
| `page` | `1` | Numer strony (≥ 1) |
| `page_size` | `10` | Liczba wyników na stronie (1–100) |

Filtry łączą się warunkiem „i”. Nieznane parametry, nieznane wartości i liczby poza zakresem są odrzucane kodem 400.

```http
GET /api/models?search=sentiment&framework=PyTorch&sort=name&order=asc&page=1&page_size=10
```

Odpowiedź `200 OK`:

```json
{
  "items": [ { "id": 3, "name": "sentiment-pl", "framework": "PyTorch", "...": "..." } ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "pages": 1
}
```

Strona poza zakresem zwraca pustą listę `items` z poprawnym `total`. Gdy nic nie pasuje, `total` i `pages` wynoszą 0.

## Historia zmian

Każde utworzenie, zmiana i usunięcie modelu zapisuje wpis. Zmiany są zapisywane razem z modelem w jednej transakcji, a `PUT` bez faktycznych zmian nie tworzy wpisu.

`GET /api/models/{id}/history` zwraca listę wpisów od najnowszego (także dla usuniętego modelu). Dla identyfikatora, który nigdy nie istniał, zwraca 404.

```json
[
  {
    "id": 7,
    "model_id": 5,
    "model_name": "iris",
    "action": "updated",
    "changes": {
      "version": { "from": "1.0.0", "to": "1.1.0" },
      "status": { "from": "draft", "to": "published" }
    },
    "user_email": "admin@example.com",
    "created_at": "2026-10-10T12:00:00Z"
  }
]
```

| Pole | Opis |
|---|---|
| `action` | `created`, `updated` lub `deleted` |
| `changes` | Dla `created`: wartości początkowe (`from` = `null`). Dla `updated`: tylko zmienione pola. Dla `deleted`: `null` |
| `user_email` | Autor zmiany (kopia adresu z chwili zmiany) |

`GET /api/history` (tylko administrator) zwraca dziennik wszystkich zmian, także usuniętych modeli, w postaci strony wyników jak w liście modeli. Parametry: `action` (`created`, `updated`, `deleted`), `model_id`, `page` (domyślnie 1), `page_size` (domyślnie 20, maks. 100).

## Pliki modeli

Każdy model może mieć jeden plik. Pliki są przechowywane w Azure Blob Storage, a API zwraca tylko ich opis (`file_name`, `file_size`, `file_sha256`).

### Wgranie lub zastąpienie pliku (administrator)

`POST /api/models/{id}/file` z ciałem `multipart/form-data` i polem `file`:

```bash
curl -X POST http://localhost:8000/api/models/1/file \
  -H "Authorization: Bearer $TOKEN" -F "file=@iris.pkl"
```

| Reguła | Wartość |
|---|---|
| Dozwolone rozszerzenia | `.pkl`, `.joblib`, `.onnx`, `.pt`, `.pth`, `.h5`, `.safetensors` (wielkość liter nie ma znaczenia) |
| Maksymalny rozmiar | `MAX_UPLOAD_MB` (domyślnie 200 MB), błąd 413 |
| Pusty plik | błąd 400 |
| Nazwa pliku | ścieżka i znaki sterujące są usuwane (`../../x.pkl` zapisze się jako `x.pkl`) |

Odpowiedź `200 OK` to model z uzupełnionymi polami pliku. Pole `size_mb` jest ustawiane na rozmiar pliku, a zmiana trafia do historii (`file_name`, `size_mb`). Przy zastąpieniu poprzedni plik jest usuwany z magazynu.

### Pobranie pliku (zalogowany użytkownik)

`GET /api/models/{id}/download` nie zwraca samego pliku, tylko krótko ważny adres do magazynu:

```json
{
  "url": "https://NAZWA.blob.core.windows.net/models/models/1/3f2a....pkl?sv=...&se=...&sp=r&sig=...",
  "file_name": "iris.pkl",
  "file_size": 3145728,
  "expires_in": 300
}
```

Adres jest ważny `expires_in` sekund (domyślnie 300), daje dostęp tylko do odczytu tego jednego obiektu i wymusza pobranie pod oryginalną nazwą (`Content-Disposition: attachment`). Przeglądarka otwiera go bezpośrednio, więc nagłówek `Authorization` nie jest tam potrzebny ani wysyłany. Model bez pliku zwraca 404.

### Usunięcie pliku (administrator)

`DELETE /api/models/{id}/file` usuwa plik z magazynu i czyści jego opis w modelu. Odpowiedź `200 OK` to model. Brak pliku zwraca 404. Usunięcie całego modelu usuwa także jego plik.

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
| `file_name` | tekst | tylko odczyt | oryginalna nazwa pliku modelu albo `null` |
| `file_size` | liczba całkowita | tylko odczyt | rozmiar pliku w bajtach albo `null` |
| `file_sha256` | tekst | tylko odczyt | suma kontrolna SHA-256 pliku albo `null` |
| `created_at` | data i czas (ISO 8601) | tylko odczyt | ustawiane przez serwer |
| `updated_at` | data i czas (ISO 8601) | tylko odczyt | aktualizowane przez serwer |

Nieznane pola w żądaniu są odrzucane (kod 400). Reguły walidacji są takie same po stronie klienta (`frontend/src/validation/`) i serwera (`backend/app/schemas/`).

## Przykłady

### Utworzenie modelu (administrator)

```http
POST /api/models
Authorization: Bearer <token administratora>
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
# logowanie i zapis tokenu (wymaga narzędzia jq)
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"TWOJE_HASLO"}' | jq -r .access_token)

curl http://localhost:8000/api/models -H "Authorization: Bearer $TOKEN"

curl -X POST http://localhost:8000/api/models \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"iris","framework":"ONNX","task":"Klasyfikacja","version":"1.0.0"}'
```

## Format błędów

Błąd walidacji (400):

```json
{
  "detail": "Nieprawidłowe dane wejściowe",
  "errors": [
    { "field": "body.password", "message": "Hasło musi mieć co najmniej 8 znaków, w tym literę i cyfrę" }
  ]
}
```

Pozostałe błędy mają postać `{ "detail": "..." }`. Odpowiedzi 401 zawierają nagłówek `WWW-Authenticate: Bearer`.

| Kod | Znaczenie | Przykład |
|---|---|---|
| 200 | OK | pobranie listy, szczegółów lub historii, aktualizacja, logowanie |
| 201 | Utworzono | poprawny `POST /api/models` lub `POST /api/auth/register` |
| 204 | Brak treści | poprawne usunięcie |
| 400 | Nieprawidłowe dane | błędny format wersji, słabe hasło, nieznane pole, błędny parametr listy (np. `page=0`), identyfikator niebędący liczbą |
| 401 | Brak uwierzytelnienia | brak tokenu, token błędny lub wygasły, złe dane logowania |
| 403 | Brak uprawnień | zwykły użytkownik próbuje dodać, zmienić lub usunąć model albo odczytać dziennik `/api/history` |
| 404 | Nie znaleziono | model lub jego plik nie istnieje |
| 409 | Konflikt | rejestracja na zajęty adres e-mail |
| 413 | Plik za duży | przesyłany plik przekracza `MAX_UPLOAD_MB` |
| 500 | Błąd serwera | nieoczekiwany wyjątek; odpowiedź zawiera ogólny komunikat, szczegóły są tylko w logach |
| 502 | Błąd magazynu | magazyn plików odrzucił operację lub jest niedostępny |
| 503 | Niedostępne | magazyn plików nie jest skonfigurowany w tym środowisku |

Uwagi:
- FastAPI domyślnie zwraca 422 dla błędów walidacji. W tym projekcie są one zamieniane na 400 (`backend/app/core/error_handlers.py`).
- Uprawnienia są sprawdzane przed walidacją danych, więc zwykły użytkownik dostaje 403 także dla niepoprawnego ciała żądania.
