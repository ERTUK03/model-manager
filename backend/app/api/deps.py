from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import get_settings
from app.core.exceptions import ForbiddenError, ServiceUnavailableError, UnauthorizedError
from app.core.roles import ROLE_ADMIN
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.history_repository import HistoryRepository
from app.repositories.ml_model_repository import SqlAlchemyMLModelRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.file_service import FileService
from app.services.history_service import HistoryService
from app.services.ml_model_service import MLModelService
from app.storage.base import FileStorage
from app.storage.factory import get_storage

# auto_error=False: brak nagłówka obsługujemy sami, żeby zwracać 401 w jednolitym formacie
bearer_scheme = HTTPBearer(auto_error=False)


def get_storage_or_none() -> FileStorage | None:
    return get_storage()


def get_file_storage() -> FileStorage:
    storage = get_storage()
    if storage is None:
        raise ServiceUnavailableError("Magazyn plików nie jest skonfigurowany")
    return storage


def get_model_service(
    db: Session = Depends(get_db), storage: FileStorage | None = Depends(get_storage_or_none)
) -> MLModelService:
    return MLModelService(SqlAlchemyMLModelRepository(db), HistoryRepository(db), storage)


def get_file_service(db: Session = Depends(get_db), storage: FileStorage = Depends(get_file_storage)) -> FileService:
    settings = get_settings()
    return FileService(
        SqlAlchemyMLModelRepository(db),
        HistoryRepository(db),
        storage,
        settings.max_upload_mb,
        settings.download_url_expire_seconds,
    )


def get_history_service(db: Session = Depends(get_db)) -> HistoryService:
    return HistoryService(HistoryRepository(db), SqlAlchemyMLModelRepository(db))


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
