from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError
from app.models.user import User


class UserRepository:
    """Jedyne miejsce, które wykonuje zapytania o użytkowników."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def add(self, email: str, hashed_password: str, role: str) -> User:
        user = User(email=email, hashed_password=hashed_password, role=role)
        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictError("Konto z tym adresem e-mail już istnieje") from None
        self.db.refresh(user)
        return user

    def set_role(self, user: User, role: str) -> User:
        user.role = role
        self.db.commit()
        self.db.refresh(user)
        return user
