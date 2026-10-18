from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    model_id: int
    model_name: str
    action: Literal["created", "updated", "deleted"]
    changes: dict | None
    user_email: str | None
    created_at: datetime


class HistoryListQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: Literal["created", "updated", "deleted"] | None = None
    model_id: int | None = Field(default=None, ge=1)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class HistoryPage(BaseModel):
    items: list[HistoryRead]
    total: int
    page: int
    page_size: int
    pages: int
