from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MLModelBase(BaseModel):
    name: str
    description: str | None = None
    framework: str
    task: str
    version: str
    accuracy: float | None = None
    size_mb: float | None = None
    status: str = "draft"


class MLModelCreate(MLModelBase):
    pass


class MLModelUpdate(MLModelBase):
    pass


class MLModelRead(MLModelBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
