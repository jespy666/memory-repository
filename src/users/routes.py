from fastapi.routing import APIRouter
from fastapi import HTTPException, status, Depends

from typing import List, Sequence, Optional, TypeVar, Union, Dict

from .schemas import UserSchema, UserUpdate
from .models import User
from .crud import UserCRUD
from src.depends import get_current_user


user_router = APIRouter(prefix='/users')

T = TypeVar('T', bound=Union[str, int])


@user_router.get('/me/', response_model=UserSchema)
async def show_me(
        current_user: User = Depends(get_current_user)
) -> User:
    """
    Show user himself.

    Args:
         current_user (User obj.): Current user from cookies.
    Returns:
        User schema.
    """
    return current_user


@user_router.get('/', response_model=List[UserSchema])
async def get_users(
        current_user: User = Depends(get_current_user)
) -> Optional[Sequence[User]]:
    """
    Getting all users from db. Require admin rights.

    Args:
        current_user (User obj.): Current user from cookies.
    Returns:
        List of users or empty list.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access denied'
        )
    crud = UserCRUD()
    users: Sequence[User] = await crud.get_all_users()
    return users if users else []



@user_router.get('/{user_id}/', response_model=UserSchema)
async def get_user(
        user_id: int,
        current_user: User = Depends(get_current_user)
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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access denied'
        )

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
        user_id: int,
        current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete user from DB. Require admin rights.

    Args:
        user_id (integer): An user ID.
        current_user (User obj.): Current user from cookies.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access denied'
        )

    crud = UserCRUD()
    await crud.delete_user('id', user_id)


@user_router.put('/{user_id}/', response_model=UserUpdate)
async def update_user(
        user_id: int,
        data: Dict[str, T],
        current_user: User = Depends(get_current_user)
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
    if not current_user.id == user_id or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access denied'
        )

    crud = UserCRUD()
    updated_user: User = await crud.update_user('id', user_id, data)
    return updated_user
