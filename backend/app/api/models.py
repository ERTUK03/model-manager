from fastapi import APIRouter, Depends, Path, Response, status

from app.api.deps import get_model_service
from app.schemas.ml_model import MLModelCreate, MLModelRead, MLModelUpdate
from app.services.ml_model_service import MLModelService

router = APIRouter(prefix="/models", tags=["models"])

ModelId = Path(ge=1, description="Identyfikator modelu")


@router.get("", response_model=list[MLModelRead])
def list_models(service: MLModelService = Depends(get_model_service)):
    return service.list_models()


@router.get("/{model_id}", response_model=MLModelRead)
def get_model(model_id: int = ModelId, service: MLModelService = Depends(get_model_service)):
    return service.get_model(model_id)


@router.post("", response_model=MLModelRead, status_code=status.HTTP_201_CREATED)
def create_model(data: MLModelCreate, service: MLModelService = Depends(get_model_service)):
    return service.create_model(data)


@router.put("/{model_id}", response_model=MLModelRead)
def update_model(
    data: MLModelUpdate,
    model_id: int = ModelId,
    service: MLModelService = Depends(get_model_service),
):
    return service.update_model(model_id, data)


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model(model_id: int = ModelId, service: MLModelService = Depends(get_model_service)):
    service.delete_model(model_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
