from typing import Optional, Dict

from fastapi.routing import APIRouter
from fastapi.responses import RedirectResponse
from fastapi import Request, Response, BackgroundTasks

from httpx import AsyncClient

from src.users.crud import UserCRUD
from src.users.schemas import UserSchema
from src.users.models import User

from src.auth.utils import generate_random_password, issue_token
from src.auth.schemas import UserCreate

from src.mail import send_welcome_google_task

from src import exceptions as exc

from src.config import settings


google_router = APIRouter(prefix='/google')


@google_router.get("/callback/")
async def google_callback(
        request: Request,
        response: Response,
        tasks: BackgroundTasks
) -> Dict[str, str]:
    """
    Endpoint to handle google auth. Create a new account if there is a signup
    with Google.
    """
    code: Optional[str] = request.query_params.get("code")
    if not code:
        raise exc.BadRequestException("Code not provided")

    # Exchange the code for an access token
    async with AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        token_data: Dict[str, str] = token_resp.json()

    if "access_token" not in token_data:
        raise exc.BadRequestException("Failed to retrieve access token")

    # Retrieve user info from Google
    google_token: str = token_data["access_token"]
    async with AsyncClient() as client:
        user_resp = await client.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {google_token}"}
        )
        user_data = user_resp.json()

    email: Optional[str] = user_data.get("email")
    if not email:
        raise exc.BadRequestException("Failed to retrieve user email")

    # Check if the user exists, create a new one otherwise
    crud = UserCRUD()
    user: Optional[User] = await crud.get_user('email', email)
    if not user:
        given_name: Optional[str] = user_data.get("given_name")
        new_user_data = UserCreate(
            email=email,
            name=given_name if given_name else email,
            password=generate_random_password()
        )
        # create and make user active initially
        new_user: UserSchema = await crud.create_user(
            new_user_data,
            active=True
        )

        # send hello email
        tasks.add_task(send_welcome_google_task,email, new_user)

    # issue access and refresh tokens
    access_token = issue_token(
        data={"sub": email},
        expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_token = issue_token(
        data={"sub": email},
        expires_delta=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )

    # setting up cookies
    response.set_cookie("access_token", access_token, httponly=True)
    response.set_cookie("refresh_token", refresh_token, httponly=True)

    return {"message": "Successful login via google oauth2"}


@google_router.get('/')
async def google_login() -> RedirectResponse:
    """
    Trigger endpoint for Google OAuth2.
    """
    return RedirectResponse(
        settings.GOOGLE_AUTH_URI.format(
            client_id=settings.GOOGLE_CLIENT_ID,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )
    )
