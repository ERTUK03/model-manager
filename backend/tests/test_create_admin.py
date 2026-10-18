import pytest

from app.core.database import Base, SessionLocal, engine
from app.core.roles import ROLE_ADMIN, ROLE_USER
from app.core.security import hash_password, verify_password
from app.repositories.user_repository import UserRepository
from scripts.create_admin import create_admin


@pytest.fixture
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        yield session
    Base.metadata.drop_all(bind=engine)


def test_creates_admin_with_hashed_password(db):
    assert create_admin(db, "Admin@Example.com", "Haslo1234") == "created"
    user = UserRepository(db).get_by_email("admin@example.com")
    assert user.role == ROLE_ADMIN
    assert user.hashed_password != "Haslo1234"
    assert verify_password("Haslo1234", user.hashed_password)


def test_is_idempotent(db):
    create_admin(db, "admin@example.com", "Haslo1234")
    assert create_admin(db, "admin@example.com", "Haslo1234") == "exists"


def test_promotes_existing_user_without_changing_password(db):
    repository = UserRepository(db)
    repository.add("jan@example.com", hash_password("Stare1234"), ROLE_USER)
    assert create_admin(db, "jan@example.com", "Nowe12345") == "promoted"
    user = repository.get_by_email("jan@example.com")
    assert user.role == ROLE_ADMIN
    assert verify_password("Stare1234", user.hashed_password)


def test_rejects_weak_password_and_bad_email(db):
    with pytest.raises(ValueError):
        create_admin(db, "admin@example.com", "krotkie")
    with pytest.raises(ValueError):
        create_admin(db, "admin@example.com", "tylkolitery")
    with pytest.raises(ValueError):
        create_admin(db, "to-nie-email", "Haslo1234")
