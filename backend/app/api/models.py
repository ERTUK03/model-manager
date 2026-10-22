from typing import Annotated

from fastapi import APIRouter, Depends, File, Path, Query, Response, UploadFile, status

from app.api.deps import get_current_user, get_file_service, get_history_service, get_model_service, require_admin
from app.models.user import User
from app.schemas.history import HistoryRead
from app.schemas.ml_model import (
    DownloadInfo,
    MLModelCreate,
    MLModelListQuery,
    MLModelPage,
    MLModelRead,
    MLModelUpdate,
)
from app.services.file_service import FileService
from app.services.history_service import HistoryService
from app.services.ml_model_service import MLModelService

# Odczyt: każdy zalogowany użytkownik. Zapis (POST, PUT, DELETE): tylko administrator
router = APIRouter(prefix="/models", tags=["models"], dependencies=[Depends(get_current_user)])

ModelId = Path(ge=1, description="Identyfikator modelu")


@router.get("", response_model=MLModelPage)
def list_models(
    params: Annotated[MLModelListQuery, Query()],
    service: MLModelService = Depends(get_model_service),
):
    return service.list_models(params)


@router.get("/{model_id}", response_model=MLModelRead)
def get_model(model_id: int = ModelId, service: MLModelService = Depends(get_model_service)):
    return service.get_model(model_id)


@router.get("/{model_id}/download", response_model=DownloadInfo)
def get_download_url(model_id: int = ModelId, service: FileService = Depends(get_file_service)):
    """Zwraca krótko ważny adres, pod którym przeglądarka pobiera plik bezpośrednio z magazynu."""
    return service.download_info(model_id)


@router.get("/{model_id}/history", response_model=list[HistoryRead])
def get_model_history(model_id: int = ModelId, service: HistoryService = Depends(get_history_service)):
    return service.list_for_model(model_id)


@router.post("", response_model=MLModelRead, status_code=status.HTTP_201_CREATED)
def create_model(
    data: MLModelCreate,
    service: MLModelService = Depends(get_model_service),
    actor: User = Depends(require_admin),
):
    return service.create_model(data, actor)


@router.put("/{model_id}", response_model=MLModelRead)
def update_model(
    data: MLModelUpdate,
    model_id: int = ModelId,
    service: MLModelService = Depends(get_model_service),
    actor: User = Depends(require_admin),
):
    return service.update_model(model_id, data, actor)


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model(
    model_id: int = ModelId,
    service: MLModelService = Depends(get_model_service),
    actor: User = Depends(require_admin),
):
    service.delete_model(model_id, actor)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{model_id}/file", response_model=MLModelRead)
def upload_model_file(
    file: Annotated[UploadFile, File(description="Plik modelu")],
    model_id: int = ModelId,
    service: FileService = Depends(get_file_service),
    actor: User = Depends(require_admin),
):
    """Dodaje plik do modelu albo zastępuje poprzedni."""
    return service.upload(model_id, file.filename, file.file, actor)


@router.delete("/{model_id}/file", response_model=MLModelRead)
def delete_model_file(
    model_id: int = ModelId,
    service: FileService = Depends(get_file_service),
    actor: User = Depends(require_admin),
):
    return service.remove(model_id, actor)
