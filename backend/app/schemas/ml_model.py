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
    created_at: datetime
    updated_at: datetime
