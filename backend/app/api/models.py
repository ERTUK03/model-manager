from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.deps import get_model_service
from app.schemas.ml_model import MLModelCreate, MLModelRead, MLModelUpdate
from app.services.ml_model_service import MLModelService

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", response_model=list[MLModelRead])
def list_models(service: MLModelService = Depends(get_model_service)):
    return service.list_models()


@router.get("/{model_id}", response_model=MLModelRead)
def get_model(model_id: int, service: MLModelService = Depends(get_model_service)):
    model = service.get_model(model_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Model nie istnieje")
    return model


@router.post("", response_model=MLModelRead, status_code=status.HTTP_201_CREATED)
def create_model(data: MLModelCreate, service: MLModelService = Depends(get_model_service)):
    return service.create_model(data)


@router.put("/{model_id}", response_model=MLModelRead)
def update_model(model_id: int, data: MLModelUpdate, service: MLModelService = Depends(get_model_service)):
    model = service.update_model(model_id, data)
    if model is None:
        raise HTTPException(status_code=404, detail="Model nie istnieje")
    return model


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model(model_id: int, service: MLModelService = Depends(get_model_service)):
    if not service.delete_model(model_id):
        raise HTTPException(status_code=404, detail="Model nie istnieje")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
