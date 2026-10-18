from functools import lru_cache

from app.core.exceptions import UnauthorizedError
from app.core.roles import ROLE_USER
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


@lru_cache
def _dummy_hash() -> str:
    # Gdy użytkownik nie istnieje, i tak weryfikujemy hasło: czas odpowiedzi nie zdradza, które e-maile mają konta
    return hash_password("dummy-password-for-timing-1")


class AuthService:
    def __init__(self, users: UserRepository):
        self.users = users

    def register(self, data: UserCreate) -> User:
        # Nowe konta zawsze dostają rolę user. Administratora tworzy scripts/create_admin.py
        return self.users.add(data.email.lower(), hash_password(data.password), ROLE_USER)

    def login(self, email: str, password: str) -> tuple[User, str]:
        user = self.users.get_by_email(email.strip().lower())
        password_ok = verify_password(password, user.hashed_password if user else _dummy_hash())
        if user is None or not password_ok:
            raise UnauthorizedError("Nieprawidłowy e-mail lub hasło")
        return user, create_access_token(user.id)
