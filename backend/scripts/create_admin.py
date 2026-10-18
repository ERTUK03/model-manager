"""Tworzy konto administratora (albo nadaje rolę admina istniejącemu użytkownikowi).
Dane pochodzą ze zmiennych środowiskowych ADMIN_EMAIL i ADMIN_PASSWORD.
Skrypt jest bezpieczny do wielokrotnego uruchamiania.

Uruchomienie (z folderu backend):  python -m scripts.create_admin"""
import sys

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.roles import ROLE_ADMIN
from app.core.security import hash_password
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


def create_admin(db: Session, email: str, password: str) -> str:
    """Zwraca: 'created', 'promoted' albo 'exists'."""
    data = UserCreate(email=email, password=password)  # walidacja adresu i siły hasła
    repository = UserRepository(db)
    user = repository.get_by_email(data.email.lower())
    if user is None:
        repository.add(data.email.lower(), hash_password(data.password), ROLE_ADMIN)
        return "created"
    if user.role != ROLE_ADMIN:
        repository.set_role(user, ROLE_ADMIN)
        return "promoted"
    return "exists"


def main() -> None:
    settings = get_settings()
    if not settings.admin_email or not settings.admin_password:
        sys.exit("Ustaw zmienne ADMIN_EMAIL i ADMIN_PASSWORD (np. w pliku .env).")
    with SessionLocal() as db:
        result = create_admin(db, settings.admin_email, settings.admin_password.get_secret_value())
    messages = {
        "created": "Utworzono konto administratora.",
        "promoted": "Istniejące konto otrzymało rolę administratora.",
        "exists": "Konto administratora już istnieje, nic nie zmieniono.",
    }
    print(messages[result])


if __name__ == "__main__":
    main()
