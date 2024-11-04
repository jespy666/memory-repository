from typing import Optional, Annotated
from annotated_types import MinLen, MaxLen

from pydantic import BaseModel, EmailStr, constr, ConfigDict


class UserSchema(BaseModel):

    model_config = ConfigDict(strict=True)

    email: EmailStr
    name: Annotated[str, MaxLen(50)]
    password: Annotated[str, MinLen(8), MaxLen(120)]
    username: Optional[str] = None
    is_active: bool = False
    is_admin: bool = False


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[constr(min_length=1, max_length=50)] = None
    name: Optional[constr(min_length=1, max_length=50)] = None


class PasswordUpdate(BaseModel):
    model_config = ConfigDict(strict=True)

    old_password: Annotated[str, MinLen(8), MaxLen(120)]
    new_password: Annotated[str, MinLen(8), MaxLen(120)]
