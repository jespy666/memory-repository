import asyncio

from fastapi.routing import APIRouter
from fastapi import HTTPException, status, Request

from typing import List, Sequence, Optional, TypeVar, Union, Dict

from src.config import settings

from src.mail import send_activation_email_task

from src.auth.utils import issue_token

from src.users.schemas import UserSchema, UserUpdate
from src.users.models import User
from src.users.crud import UserCRUD

from src.depends import user_dependency

from src import exceptions as exc


user_router = APIRouter(prefix='/users')

T = TypeVar('T', bound=Union[str, int])


@user_router.get('/me/', response_model=UserSchema)
async def show_me(current_user: user_dependency, request: Request) -> User:
    """
    Show user himself.

    Args:
        current_user (User obj.): Current user from cookies.
        request: Starlette request object.
    Returns:
        User schema.
    """
    # assume user is active, raise exc otherwise
    if current_user.is_active is False:
        email: str = current_user.email
        activation_token: str = issue_token(
            data={'sub': email},
            expires_delta=settings.ACTIVATE_TOKEN_EXPIRE_MINUTES
        )

        # send confirmation letter again
        asyncio.create_task(
                send_activation_email_task(
                request,
                email,
                activation_token
            )
        )

        raise exc.NonActiveUserException

    return current_user


@user_router.get('/', response_model=List[UserSchema])
async def get_users(current_user: user_dependency) -> Optional[Sequence[User]]:
    """
    Getting all users from db. Require admin rights.

    Args:
        current_user (User obj.): Current user from cookies.
    Returns:
        List of users or empty list.
    """
    if not current_user.is_admin:
        raise exc.AccessDeniedException

    crud = UserCRUD()
    users: Sequence[User] = await crud.get_all_users()
    return users if users else []



@user_router.get('/{user_id}/', response_model=UserSchema)
async def get_user(
        current_user: user_dependency,
        user_id: int
) -> User:
    """
    Getting user by user id. Require admin rights.

    Args:
        user_id (integer): User ID.
        current_user (User obj.): Current user from cookies.
    Returns:
        Current user.
    """

    if not current_user.is_admin:
        raise exc.AccessDeniedException

    crud = UserCRUD()
    user: Optional[User] = await crud.get_user('id', user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    return user


@user_router.delete('/{user_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        current_user: user_dependency,
        user_id: int
) -> None:
    """
    Delete user from DB. Require admin rights.

    Args:
        user_id (integer): An user ID.
        current_user (User obj.): Current user from cookies.
    """
    if not current_user.is_admin:
        raise exc.AccessDeniedException

    crud = UserCRUD()
    await crud.delete_user('id', user_id)


@user_router.put('/{user_id}/', response_model=UserUpdate)
async def update_user(
        current_user: user_dependency,
        user_id: int,
        data: Dict[str, T]
) -> User:
    """
    Update user fields. Personality required.

    Args:
        user_id (integer): An user ID.
        data (dictionary): Updated user fields.
        current_user (User obj): Current user from cookies.
    Raises:
        HTTPException: If user trying to change another user or user does not
        exist.
    """
    if not (current_user.id == user_id or current_user.is_admin):
        raise exc.AccessDeniedException

    crud = UserCRUD()
    updated_user: User = await crud.update_user('id', user_id, data)
    return updated_user
