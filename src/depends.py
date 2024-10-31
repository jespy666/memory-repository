from typing import Optional, Annotated

from fastapi import HTTPException, Request, Depends, Response
from fastapi.security import OAuth2PasswordBearer

from src.auth.utils import issue_token
from src.auth.utils import verify_token

from src.users.crud import UserCRUD
from src.users.models import User

from src.config import settings

from src import exceptions as exc


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login/')


async def get_current_user(request: Request, response: Response) -> User:
    """
    Getting current user and checking out the access and refresh JWT tokens.
    Re-issue a new access token if refresh token still valid.

    Args:
        request (Request object): Starlette request object.
        response (Response object): Starlette response object.
    Returns:
        User object if all checks passed.
    Raises:
        HTTPException:
            cases:
                - Refresh token is missing, invalid or expired.
                - Access token is missing or invalid.
                - User account is not active.
    """
    # getting tokens from cookies
    access_token: Optional[str] = request.cookies.get('access_token')
    refresh_token: Optional[str] = request.cookies.get('refresh_token')
    # check refresh token getting from cookies
    if not refresh_token:
        raise exc.InvalidTokenException

    email: Optional[str] = await verify_token(refresh_token)

    # check refresh token is valid
    if not email:
        raise exc.InvalidTokenException

    crud = UserCRUD()
    # check access token is valid
    try:
        email: Optional[str] = await verify_token(access_token)
        user: Optional[User] = await crud.get_user('email', email)
        # check user exists
        if not user:
            raise exc.UserNotFoundException

        # well done, return current user
        return user
    except HTTPException as e:
        # access token expired case
        if e.detail == "Token expired":
            # generate new access token
            new_access_token = issue_token(
                data={"sub": email},
                expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            # update response with new token cookie
            response.set_cookie(
                key="access_token",
                value=new_access_token,
                httponly=True
            )
            user: Optional[User] = await crud.get_user('email', email)
            if not user:
                raise exc.UserNotFoundException
            return user
        else:
            # raise other errors if there are
            raise e


user_dependency = Annotated[dict, Depends(get_current_user)]
