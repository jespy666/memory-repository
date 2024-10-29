import jwt

from datetime import datetime, timedelta, timezone
from typing import Dict, TypeVar, Union

from passlib.context import CryptContext

from fastapi import HTTPException, status

from src.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

V = TypeVar('V', bound=Union[str, int])


def hash_password(password: str) -> str:
    """
    Hashed user password.

    Args:
        password (string): Source user password.
    Returns:
        Hashed user password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify hashed user password.

    Args:
        plain_password (string): Source user password.
        hashed_password (string): Hashed source user password.
    Returns:
        True if passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, V], expires_delta: int = None):
    """
    Generate access jwt token.

    Args:
        data (dictionary): User info.
        expires_delta (optional): Expire token time in minutes.
    Returns:
        Activation token as string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + timedelta(expires_delta)
    else:
        expire = (
            datetime.now(tz=timezone.utc)
            +
            timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
        )
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> str:
    """
    Verify JWT token

    Args:
        token (string): JWT token.
    Returns:
        Email addr as string.
    Raises:
        ExpiredSignatureError: If JWT token expired.
        InvalidTokenError: If JWT token is invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload.get('sub')
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
