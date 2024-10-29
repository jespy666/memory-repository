from typing import Optional

from fastapi import HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

from src.auth.utils import verify_token
from src.users.crud import UserCRUD
from src.users.models import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login/')


async def get_current_user(request: Request) -> User:
    """
    Getting current user.

    Args:
        request (Request object): FastAPI request object.
    Returns:
        User object.
    Raises:
        HTTPException: If user not found, if user not authenticated, if jwt
        token is invalid.
    """
    access_token: Optional[str] = request.cookies.get('access_token')
    email: Optional[str] = verify_token(access_token)
    # Check if jwt token is valid
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid auth credentials'
        )
    crud = UserCRUD()
    user: Optional[User] = await crud.get_user('email', email)
    # check if user does not exist
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    return user
