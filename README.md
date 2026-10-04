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
