from typing import Optional, Dict, Annotated

from fastapi import HTTPException, status, Request, Depends, BackgroundTasks
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from src.users.crud import UserCRUD
from src.users.models import User
from src.users.schemas import UserSchema

from src.mail import (
    send_activation_email_task,
    send_welcome_msg_task
)

from src.auth.schemas import UserCreate, Token
from src.auth.utils import verify_token, issue_token, verify_password

from src.config import settings

from src import exceptions as exc


auth_router = APIRouter()


@auth_router.post(
    '/signup/',
    response_model=UserCreate,
    status_code=status.HTTP_201_CREATED
)
async def sign_up(
        user: UserCreate,
        request: Request,
        background_tasks: BackgroundTasks
) -> UserSchema:
    """
    Registration endpoint.

    Args:
        user (UserCreate): User schema for sign up.
        request: A Starlette request object.
        background_tasks: FastAPI background tasks object.
    Returns:
        UserCreate: Created user data without password.
    """
    crud = UserCRUD()
    existed: Optional[User] = await crud.get_user(
        'email',
        user.email
    )
    if existed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User with same email already exist'
        )
    new_user: UserSchema = await crud.create_user(user)
    activation_token: str = issue_token(
        data={'sub': new_user.email},
        expires_delta=settings.ACTIVATE_TOKEN_EXPIRE_MINUTES
    )
    # send activation email
    background_tasks.add_task(
        send_activation_email_task,
        request,
        new_user.email,
        activation_token
    )
    return new_user


@auth_router.get('/activate/')
async def activate_account(
        token: str,
        background_tasks: BackgroundTasks
) -> Dict[str, str]:
    """
    User activation endpoint.

    Args:
        token (string): JWT token from email link.
        background_tasks: FastAPI background tasks object.
    Raises:
        HTTPException: If impossible to decode a token.
        HTTPException: If impossible to find a user.
    """
    email: Optional[str] = await verify_token(token)
    if not email:
        raise exc.InvalidTokenException
    crud = UserCRUD()
    await crud.update_user('email', email, data={'is_active': True})

    # send welcome letter
    background_tasks.add_task(send_welcome_msg_task, email)
    return {
        'message': 'Your account is active now!'
    }


@auth_router.post('/login/', response_model=Token)
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> JSONResponse:
    """
    Login endpoint.

    Args:
        form_data (form): OAuth2 Form.
    Returns:
        Token schema.
    """
    crud = UserCRUD()
    user: Optional[User] = await crud.get_user(
        'email',
        form_data.username
    )
    if not user:
        raise exc.UserNotFoundException
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Wrong password'
        )
    access_token = issue_token(
        data={"sub": form_data.username},
        expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_token = issue_token(
        data={"sub": form_data.username},
        expires_delta=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )

    response = JSONResponse(content={"message": "Login success"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        expires=7200
    )
    return response
