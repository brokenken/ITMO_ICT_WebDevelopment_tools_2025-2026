from datetime import datetime
from typing import Annotated

from pydantic import EmailStr, Field, StringConstraints, field_validator

from app.schemas.common import PatchSchema, Schema

Username = Annotated[
    str, StringConstraints(strip_whitespace=True, to_lower=True, pattern=r"^[a-z0-9_]{3,50}$")
]
FullName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Password = Annotated[str, Field(min_length=8, max_length=128)]


class Register(Schema):
    username: Username
    email: EmailStr = Field(max_length=254)
    full_name: FullName
    password: Password

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class UserPublic(Schema):
    id: int
    username: str
    full_name: str


class UserRead(UserPublic):
    email: str
    created_at: datetime


class UserPatch(PatchSchema):
    full_name: FullName | None = None


class PasswordChange(Schema):
    current_password: Password
    new_password: Password


class Token(Schema):
    access_token: str
    token_type: str = "bearer"
