# Model Manager

Aplikacja webowa do zarządzania i pobierania zapisanych modeli uczenia maszynowego. Użytkownik loguje się, przegląda katalog modeli, sprawdza ich szczegóły (framework, wersja, metryki) i pobiera pliki na swój komputer. Administrator dodaje, edytuje i usuwa modele.

Projekt zrealizowany w architekturze 3-warstwowej i wdrożony w chmurze Azure.

## Funkcjonalności

- Rejestracja i logowanie użytkownika (JWT)
- Lista modeli oraz widok szczegółowy pojedynczego modelu
- Operacje CRUD na modelach (tworzenie, edycja, usuwanie)
- Walidacja danych po stronie klienta i serwera
- Komunikacja front-end ↔ back-end przez REST API
- Wyszukiwanie i filtrowanie listy modeli
- Statusy modeli (`draft`, `published`, `archived`) i historia zmian
- Obsługa błędów i komunikaty dla użytkownika
- Integracja z usługą chmurową: przechowywanie plików modeli w Azure Blob Storage, pobieranie przez podpisane URL

## Architektura

<img width="540" height="352" alt="diagram" src="https://github.com/user-attachments/assets/495c27dc-29b6-4c9e-ba5e-919bf0b67cc0" />

### Przepływ danych (3-tier)

<img width="2720" height="2200" alt="architektura_3_tier_warstwa_aplikacji" src="https://github.com/user-attachments/assets/3af3d2dd-b640-4189-88e1-296339b3206c" />

### Separacja sieciowa

Wszystkie elementy działają w jednej sieci wirtualnej, w osobnych podsieciach. Ruch między nimi kontrolują reguły NSG.

## Stack technologiczny

| Obszar | Technologia |
|---|---|
| Front-end | React (Vite), React Router, React Hook Form + Zod |
| Back-end | Python, FastAPI, Pydantic, SQLAlchemy, Alembic |
| Baza danych | PostgreSQL |
| Autoryzacja | JWT, bcrypt |
| Pliki | Azure Blob Storage |
| Kontenery | Docker |
| Chmura | Microsoft Azure |

## Struktura repozytorium

```
.
├── README.md        główny przewodnik po projekcie
├── backend/         API (FastAPI): routers, services, repositories, models, schemas
├── frontend/        aplikacja React
├── config/          pliki konfiguracyjne (.env.example, nginx, skrypty wdrożenia)
└── docs/            dokumentacja, diagramy, zrzuty ekranu
```
## Konfiguracja

Cała konfiguracja pochodzi ze zmiennych środowiskowych. W kodzie nie ma adresów, haseł ani kluczy. Pliki `.env` i `.env.local` są w `.gitignore`, a w repozytorium są tylko wzory `.env.example`.

**Back-end** (`backend/.env`, wzór: `backend/.env.example`)

| Zmienna | Opis |
|---|---|
| `DATABASE_URL` | Connection string do bazy PostgreSQL (wymagana, bez niej aplikacja się nie uruchomi) |
| `APP_ENV` | Nazwa środowiska, domyślnie `development` |
| `CORS_ORIGINS` | Dozwolone źródła CORS, oddzielone przecinkami (puste, gdy ruch idzie przez nginx) |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Tylko dla lokalnej bazy z `docker-compose.dev.yml` |

**Front-end** (`frontend/.env.local`, wzór: `frontend/.env.example`)

| Zmienna | Opis |
|---|---|
| `VITE_API_URL` | Adres API, domyślnie ścieżka względna `/api` |
| `VITE_USE_MOCK` | `true` = dane z pliku JSON (tylko odczyt), `false` = prawdziwe API |
| `DEV_PROXY_TARGET` | Tylko `npm run dev`: dokąd Vite przekazuje `/api` |
| `BACKEND_URL` | Tylko kontener nginx: adres back-endu, do którego trafia ruch `/api` |

## Uruchomienie lokalne

Wymagania: Python 3.12, Node.js 20 (LTS), Docker Desktop.

### 1. Baza danych

```bash
cd backend
cp .env.example .env        # uzupełnij POSTGRES_* oraz DATABASE_URL (to samo hasło w obu miejscach)
docker compose -f docker-compose.dev.yml up -d
```

### 2. Back-end

```bash
python -m venv .venv
source .venv/bin/activate   # Windows (PowerShell): .\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
alembic upgrade head        # tworzy tabele
python -m scripts.seed      # opcjonalnie: 6 przykładowych modeli
uvicorn app.main:app --reload
```

API działa pod `http://localhost:8000`, a Swagger pod `http://localhost:8000/api/docs`.

### 3. Front-end

```bash
cd frontend
cp .env.example .env.local  # ustaw DEV_PROXY_TARGET=http://localhost:8000
npm install
npm run dev
```

Aplikacja jest dostępna pod adresem wypisanym przez Vite (zwykle `http://localhost:5173`).

### 4. Testy

```bash
cd backend && pytest        # testy API, używają osobnej bazy SQLite
cd frontend && npm test     # testy walidacji formularzy
```

## API

Pełna dokumentacja (pola, reguły walidacji, przykłady, format błędów): [docs/api.md](docs/api.md). Interaktywna wersja: `/api/docs`.

| Metoda | Ścieżka | Opis | Kod |
|---|---|---|---|
| `GET` | `/api/health` | Stan API | 200 |
| `GET` | `/api/models` | Lista modeli | 200 |
| `GET` | `/api/models/{id}` | Szczegóły modelu | 200 |
| `POST` | `/api/models` | Utworzenie modelu | 201 |
| `PUT` | `/api/models/{id}` | Aktualizacja modelu | 200 |
| `DELETE` | `/api/models/{id}` | Usunięcie modelu | 204 |

Błędy: 400 (nieprawidłowe dane), 404 (nie znaleziono), 500 (błąd serwera).
