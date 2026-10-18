from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_settings
from app.core.security import ALGORITHM, create_access_token

CREDENTIALS = {"email": "jan@example.com", "password": "Haslo1234"}


def register(client, **overrides):
    return client.post("/api/auth/register", json={**CREDENTIALS, **overrides})


def login(client, **overrides):
    return client.post("/api/auth/login", json={**CREDENTIALS, **overrides})


def test_register_returns_201_without_password(client):
    response = register(client)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "jan@example.com"
    assert body["role"] == "user"
    assert "password" not in body and "hashed_password" not in body


def test_register_normalizes_email_case(client):
    register(client, email="  Jan@Example.COM ")
    assert login(client).status_code == 200


def test_register_duplicate_email_returns_409(client):
    register(client)
    response = register(client, email="JAN@example.com")
    assert response.status_code == 409
    assert response.json() == {"detail": "Konto z tym adresem e-mail już istnieje"}


def test_register_ignores_requested_role(client):
    response = client.post("/api/auth/register", json={**CREDENTIALS, "role": "admin"})
    assert response.status_code == 400  # nieznane pole jest odrzucane


def test_register_validation_returns_400(client):
    assert register(client, email="to-nie-email").status_code == 400
    assert register(client, password="Kr0tkie").status_code == 400
    weak = register(client, password="tylkolitery")
    assert weak.status_code == 400
    assert weak.json()["errors"][0]["message"] == "Hasło musi mieć co najmniej 8 znaków, w tym literę i cyfrę"
    assert register(client, password="12345678").status_code == 400


def test_login_returns_token_and_user(client):
    register(client)
    response = login(client)
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == "jan@example.com"


def test_login_wrong_credentials_return_401_with_same_message(client):
    register(client)
    wrong_password = login(client, password="Zle123456")
    unknown_user = login(client, email="nikt@example.com")
    assert wrong_password.status_code == unknown_user.status_code == 401
    assert wrong_password.json() == unknown_user.json() == {"detail": "Nieprawidłowy e-mail lub hasło"}
    assert wrong_password.headers["www-authenticate"] == "Bearer"


def test_me_returns_current_user(client):
    register(client)
    token = login(client).json()["access_token"]
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "jan@example.com"


def test_me_without_token_returns_401(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Wymagane uwierzytelnienie"}


def test_me_with_invalid_token_returns_401(client):
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer to-nie-jest-token"})
    assert response.status_code == 401


def test_me_with_expired_token_returns_401(client):
    register(client)
    now = datetime.now(timezone.utc)
    expired = jwt.encode(
        {"sub": "1", "iat": now - timedelta(hours=2), "exp": now - timedelta(hours=1)},
        get_settings().jwt_secret.get_secret_value(),
        algorithm=ALGORITHM,
    )
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired}"}).status_code == 401


def test_me_with_token_signed_by_other_secret_returns_401(client):
    register(client)
    forged = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        "inny-sekret-o-dlugosci-co-najmniej-32-znakow",
        algorithm=ALGORITHM,
    )
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {forged}"}).status_code == 401


def test_token_of_deleted_user_returns_401(client):
    # Token poprawny, ale użytkownik o tym id nie istnieje
    token = create_access_token(9999)
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401
