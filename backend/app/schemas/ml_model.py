from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Framework(str, Enum):
    SKLEARN = "scikit-learn"
    XGBOOST = "XGBoost"
    PYTORCH = "PyTorch"
    TENSORFLOW = "TensorFlow"
    ONNX = "ONNX"
    OTHER = "Other"


class MLModelBase(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,  # usuwa spacje z początku i końca tekstów
        use_enum_values=True,
        extra="forbid",             # nieznane pola w żądaniu są błędem
    )

    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    framework: Framework
    task: str = Field(min_length=2, max_length=50)
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$", examples=["1.0.0"])
    accuracy: float | None = Field(default=None, ge=0, le=1)
    size_mb: float | None = Field(default=None, ge=0)
    status: Literal["draft", "published", "archived"] = "draft"


class MLModelCreate(MLModelBase):
    pass


class MLModelUpdate(MLModelBase):
    pass


class MLModelRead(MLModelBase):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: int
    file_name: str | None = None
    file_size: int | None = None
    file_sha256: str | None = None
    created_at: datetime
    updated_at: datetime


class MLModelListQuery(BaseModel):
    """Parametry listy modeli: wyszukiwanie, filtry, sortowanie i paginacja."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, use_enum_values=True)

    search: str | None = Field(default=None, max_length=100, description="Fragment nazwy lub opisu")
    framework: Framework | None = None
    status: Literal["draft", "published", "archived"] | None = None
    sort: Literal["created_at", "updated_at", "name", "accuracy", "size_mb"] = "created_at"
    order: Literal["asc", "desc"] = "desc"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class MLModelPage(BaseModel):
    items: list[MLModelRead]
    total: int
    page: int
    page_size: int
    pages: int


class DownloadInfo(BaseModel):
    url: str
    file_name: str
    file_size: int | None
    expires_in: int
