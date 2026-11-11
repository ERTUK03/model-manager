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

## Bezpieczeństwo sieci i szyfrowanie ruchu

Aplikacja ma trzy warstwy: **Web** (front-end), **App** (back-end API) i **DB** (PostgreSQL). Subskrypcja studencka pozwala na jedno środowisko Container Apps na region, więc Web i App działają w jednym środowisku w podsieci `snet-web`. Rozdziela je ingress: front-end ma ingress zewnętrzny, a back-end wewnętrzny. Baza leży w osobnej, prywatnej podsieci `snet-db`. Reguły zapory są opisane w `config/azure/` i sprawdzane automatycznie skryptem `04-verify-security.sh`.

### Reguły przychodzące (Inbound)

| # | Warstwa | Źródło | Cel i port | Akcja | Gdzie wymuszone | Uwagi |
|---|---|---|---|---|---|---|
| W1 | Web | Internet | 443/TCP (HTTPS) | Allow | `nsg-web` (priorytet 100), ingress zewnętrzny | certyfikat zarządzany przez Azure |
| W2 | Web | Internet | 80/TCP (HTTP) | Allow, odpowiedź to przekierowanie na HTTPS | `nsg-web` (100), ingress (`allowInsecure=false`) | żadna treść nie jest serwowana po HTTP |
| W3 | Web | Internet | 22, 3389 (SSH, RDP) | Deny | `nsg-web` (110) | w kontenerach nie ma usług SSH ani RDP |
| W4 | Web | Pozostały ruch z Internetu | dowolny | Deny | reguła domyślna `DenyAllInBound` (65500) | |
| A1 | App | Aplikacje tego samego środowiska (nginx front-endu) | ingress wewnętrzny, HTTP | Allow | ingress wewnętrzny Container Apps | back-end jest osiągalny pod nazwą `ca-backend` tylko wewnątrz środowiska |
| A2 | App | Internet | dowolny | brak trasy | `ingress.external=false` | API jest dostępne publicznie wyłącznie przez `/api` front-endu |
| A3 | App | Internet | 22, 3389 | Deny | `nsg-web` (110) i `nsg-app` (110) | `nsg-app` chroni zarezerwowaną, pustą podsieć |
| D1 | DB | Podsieć z back-endem `10.0.0.0/23` | 5432/TCP | Allow | `nsg-db` (100) | jedyna dozwolona ścieżka do bazy |
| D2 | DB | Internet (0.0.0.0/0) i pozostałe podsieci | dowolny, w tym 5432 i 3306 | Deny | `nsg-db` (4000) | blokuje też domyślną regułę `AllowVnetInBound` |
| D3 | DB | Internet | 22, 3389 | Deny | `nsg-db` (110) | |
| D4 | DB | cały Internet | publiczny punkt końcowy | brak | `publicNetworkAccess=Disabled` | serwer działa wyłącznie w prywatnej podsieci |

Zasada najmniejszych uprawnień obejmuje też tożsamości: kontenery pobierają obrazy rolą AcrPull, back-end ma dostęp tylko do jednego konta magazynu, a kontener działa jako zwykły użytkownik.

### Reguły wychodzące (Outbound)

W projekcie nie ma własnych reguł wychodzących: obowiązują domyślne reguły NSG (`AllowVnetOutBound`, `AllowInternetOutBound`, `DenyAllOutBound`). Środowisko Container Apps i PostgreSQL potrzebują ruchu platformowego (rejestr obrazów, monitoring), więc zbyt restrykcyjne reguły mogłyby uniemożliwić ich działanie. Poniżej zestawienie faktycznych połączeń wychodzących:

| Warstwa | Cel | Port | Szyfrowanie | Uwagi |
|---|---|---|---|---|
| Web | back-end `ca-backend` (ingress wewnętrzny) | 80/TCP | HTTP wewnątrz środowiska | brak trasy z Internetu |
| Web, App | Azure Container Registry | 443/TCP | TLS | pobieranie obrazów tożsamością zarządzaną |
| App | PostgreSQL w `snet-db` | 5432/TCP | TLS (`sslmode=require`) | jedyny ruch do bazy, patrz D1 |
| App | Azure Blob Storage | 443/TCP | TLS | zapis plików modeli |
| App | Microsoft Entra ID | 443/TCP | TLS | token tożsamości zarządzanej |
| DB | brak połączeń inicjowanych przez aplikację | | | kopie zapasowe zarządza platforma |

### Szyfrowanie ruchu

| Połączenie | Szyfrowanie | Uwagi |
|---|---|---|
| Przeglądarka do front-endu | HTTPS (TLS 1.2 lub nowszy), certyfikat zarządzany przez Azure | żądanie HTTP dostaje przekierowanie na HTTPS, a nagłówek HSTS każe przeglądarce używać tylko HTTPS |
| Front-end do back-endu | HTTP wewnątrz środowiska Container Apps | ruch nie opuszcza środowiska, ingress jest wewnętrzny |
| Back-end do PostgreSQL | TLS (`sslmode=require`) | |
| Back-end do Blob Storage | HTTPS, minimalnie TLS 1.2 | |
| Przeglądarka do Blob Storage (pobieranie pliku) | HTTPS i podpis SAS ważny 5 minut | |
| GitHub Actions do Azure | HTTPS, uwierzytelnianie OIDC | brak haseł w sekretach |

Front-end dodatkowo wysyła nagłówki `Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options` i `Referrer-Policy` oraz nie ujawnia wersji serwera.

### Weryfikacja

Automatyczna weryfikacja (reguły z uwzględnieniem priorytetów, izolacja bazy, ingress, HTTPS i certyfikat, przekierowanie, nagłówki, magazyn plików) w Azure Cloud Shell:

```bash
cd config/azure
./04-verify-security.sh
```

Skrypt wypisuje PASS lub FAIL dla każdego sprawdzenia i kończy się kodem większym od zera przy błędzie. Logikę oceny reguł zapory testują testy jednostkowe: `python3 -m unittest test_audit_nsg -v` (w katalogu `config/azure`).
