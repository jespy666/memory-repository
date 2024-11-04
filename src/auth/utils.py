import secrets

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
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify hashed user password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_random_password(length: int = 12) -> str:
    """
    Generate random password. Initial length - 12 symbols.
    """
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def issue_token(data: Dict[str, V], expires_delta: int) -> str:
    """
    Generate new jwt token (access or refresh).

    Args:
        data (dictionary): User info.
        expires_delta (optional): Expire token time in minutes.
    Returns:
        JWT token as string.
    """
    # copy source dict
    to_encode = data.copy()
    # set expire date and time
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=expires_delta)
    to_encode.update({"exp": int(expire.timestamp())})
    # issue a new token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def verify_token(token: str) -> str:
    """
    Verify JWT token validity.

    Args:
        token (string): JWT token.
    Returns:
        Email addr as string.
    Raises:
        HTTPException: If JWT token expired or JWT token is invalid.
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
