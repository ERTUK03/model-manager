from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.roles import ROLE_ADMIN
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.ml_model_repository import SqlAlchemyMLModelRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.ml_model_service import MLModelService

# auto_error=False: brak nagłówka obsługujemy sami, żeby zwracać 401 w jednolitym formacie
bearer_scheme = HTTPBearer(auto_error=False)


def get_model_service(db: Session = Depends(get_db)) -> MLModelService:
    return MLModelService(SqlAlchemyMLModelRepository(db))


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise UnauthorizedError("Wymagane uwierzytelnienie")
    user = UserRepository(db).get_by_id(decode_access_token(credentials.credentials))
    if user is None:
        raise UnauthorizedError("Token jest nieprawidłowy lub wygasł")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != ROLE_ADMIN:
        raise ForbiddenError("Brak uprawnień do wykonania tej operacji")
    return user
