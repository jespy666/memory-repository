from typing import Annotated

from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    name: Annotated[str, MinLen(3), MaxLen(20)]
    password: Annotated[str, MinLen(8), MaxLen(120)]


class Token(BaseModel):
    access_token: str
    token_type: str
