from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field, field_validator

PASSWORD_POLICY_MESSAGE = "Hasło musi mieć co najmniej 8 znaków, w tym literę i cyfrę"

# Spacje wokół adresu e-mail są usuwane przed walidacją (hasła nie zmieniamy)
Email = Annotated[EmailStr, BeforeValidator(lambda v: v.strip() if isinstance(v, str) else v)]


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: Email
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_must_contain_letter_and_digit(cls, value: str) -> str:
        if not any(c.isalpha() for c in value) or not any(c.isdigit() for c in value):
            raise ValueError(PASSWORD_POLICY_MESSAGE)
        return value


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: str
    created_at: datetime
