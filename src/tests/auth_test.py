import pytest

from unittest.mock import AsyncMock, patch

from fastapi import status

from src.auth.schemas import UserCreate
from src.auth.utils import hash_password


@pytest.mark.asyncio
@patch("src.users.crud.UserCRUD.get_user", new_callable=AsyncMock)
@patch("src.users.crud.UserCRUD.create_user", new_callable=AsyncMock)
@patch("src.mail.send_activation_email", new_callable=AsyncMock)
@pytest.mark.parametrize("user_data, expected_status, expected_email", [
    (
        {
            "email": "test1@mail.com",
            "password": "secret_password",
            "name": "name1"
        },
        status.HTTP_201_CREATED,
        "test1@mail.com"
    ),
    (
        {
            "email": "test2@mail.com",
            "password": "another_password",
            "name": "name2"
        },
        status.HTTP_201_CREATED,
        "test2@mail.com"
    ),
    (
        {
            "email": "existing_user@mail.com",
            "password": "secret_password",
            "name": "name3"
        },
        status.HTTP_400_BAD_REQUEST,
        None
    ),
])
async def test_signup(
        mock_send_email,
        mock_create_user,
        mock_get_user,
        client,
        user_data,
        expected_status,
        expected_email
):
    """
    Testing parametrized cases for signup endpoint.
    """
    if expected_status == status.HTTP_201_CREATED:
        mock_get_user.return_value = None
        mock_create_user.return_value = UserCreate(
            email=user_data["email"],
            password=user_data["password"],
            name=user_data["name"]
        )
    else:
        mock_get_user.return_value = UserCreate(
            email="existing_user@mail.com",
            password="secret_password",
            name="name3"
        )

    response = await client.post(
        "/signup/",
        json=user_data
    )

    assert response.status_code == expected_status
    if expected_email:
        assert response.json()["email"] == expected_email
    else:
        assert "email" not in response.json()
    mock_create_user.assert_called_once() if (
        expected_status == status.HTTP_201_CREATED) else (
        mock_create_user.assert_not_called()
    )
    mock_send_email.assert_called_once() if (
        expected_status == status.HTTP_201_CREATED
    ) else (
        mock_send_email.assert_not_called()
    )


@pytest.mark.asyncio
@patch("src.auth.routes.verify_token", new_callable=AsyncMock)
@patch("src.auth.routes.send_welcome_msg_task", new_callable=AsyncMock)
@patch("src.auth.routes.UserCRUD.update_user", new_callable=AsyncMock)
@pytest.mark.parametrize(
    "exp_token, exp_status, exp_json",
    [
        (
            "valid",
            status.HTTP_200_OK,
            {"message": "Your account is active now!"}
        ),
        (
            "expired",
            status.HTTP_401_UNAUTHORIZED,
            {"detail": "Token is invalid or missing"}
        ),
    ]
)
async def test_activation(
        mock_update_user,
        mock_send_welcome_msg_task,
        mock_verify_token,
        client,
        exp_token,
        exp_status,
        exp_json
):
    """
    Testing activation endpoint.
    """
    if exp_token == 'valid':
        mock_verify_token.return_value = 'true666@mail.com'
    else:
        mock_verify_token.return_value = None

    response = await client.get(
        f'/activate/?token={exp_token}'
    )
    assert response.status_code == exp_status
    assert response.json() == exp_json

    mock_update_user.assert_called_once() if (
        exp_status == status.HTTP_200_OK) else (
        mock_update_user.assert_not_called()
    )
    mock_send_welcome_msg_task.assert_called_once() if (
        exp_status == status.HTTP_200_OK
    ) else (
        mock_send_welcome_msg_task.assert_not_called()
    )


@pytest.mark.asyncio
@patch("src.auth.routes.UserCRUD.get_user", new_callable=AsyncMock)
@pytest.mark.parametrize(
    "exp_username, exp_password, exp_status, exp_json",
    [
        (
            'valid@mail.com',
            'valid_password',
            status.HTTP_200_OK,
            {"message": "Login success"}
        ),
        (
            'wrong@mail.com',
            'valid_password',
            status.HTTP_404_NOT_FOUND,
            {"detail": "User not found"}
        ),
        (
            'valid@mail.com',
            'wrong_password',
            status.HTTP_401_UNAUTHORIZED,
            {"detail": "Wrong password"}
        ),
    ]
)
async def test_login(
        mock_get_user,
        client,
        exp_username,
        exp_password,
        exp_status,
        exp_json
):
    """
    Testing login endpoint.
    """
    if exp_username == 'wrong@mail.com':
        user_data = None
    else:
        user_data = UserCreate(
            email="valid@mail.com",
            password=hash_password("valid_password"),
            name="name"
        )

    mock_get_user.return_value = user_data


    response = await client.post(
        '/login/',
        data={"username": exp_username, "password": exp_password}
    )

    assert response.status_code == exp_status
    assert response.json() == exp_json
