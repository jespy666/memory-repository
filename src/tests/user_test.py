import pytest

from unittest.mock import AsyncMock, patch

from fastapi import status

from src.auth.utils import hash_password

from src import User


ACTIVE_USER_EXP_JSON = {
    'email': 'valid@mail.com',
    'name': 'valid',
    'password': 'valid_password',
    'username': 'valid_username',
    'is_active': True,
    'is_admin': False
}

@pytest.mark.asyncio
@patch("src.users.routes.send_activation_email_task", new_callable=AsyncMock)
@pytest.mark.parametrize(
    "mock_user_dependency, exp_status, exp_json",
    [
        (
            "not_active",
            status.HTTP_403_FORBIDDEN,
            {'detail': 'Account is inactive, check your email'}
        ),
        (
            "active",
            status.HTTP_200_OK,
            ACTIVE_USER_EXP_JSON
        ),
    ],
    indirect=["mock_user_dependency"]
)
async def test_show_me(
        mock_send_activation_email_task,
        client,
        mock_user_dependency,
        exp_status,
        exp_json
):
    """
    Test getting self info (active user required).
    """
    response = await client.get('/users/me/')
    assert response.status_code == exp_status
    assert response.json() == exp_json
    mock_send_activation_email_task.assert_called_once() if (
            exp_status == status.HTTP_403_FORBIDDEN
    ) else mock_send_activation_email_task.assert_not_called()


@pytest.mark.asyncio
@patch("src.users.routes.UserCRUD.get_all_users", new_callable=AsyncMock)
@pytest.mark.parametrize(
    "mock_user_dependency, exp_status, exp_json",
    [
        (
            "admin",
            status.HTTP_200_OK,
            []
        ),
        (
            "active",
            status.HTTP_403_FORBIDDEN,
            {'detail': 'Access denied'}
        ),
    ],
    indirect=["mock_user_dependency"]
)
async def test_get_all_users(
        mock_get_all_users,
        client,
        mock_user_dependency,
        exp_status,
        exp_json
):
    """
    Test getting all users (admin required).
    """
    response = await client.get('/users/')

    assert response.status_code == exp_status
    assert response.json() == exp_json

    mock_get_all_users.assert_called_once() if (
        response.status_code == status.HTTP_200_OK
    ) else mock_get_all_users.assert_not_called()


@pytest.mark.asyncio
@patch("src.users.routes.UserCRUD.get_user", new_callable=AsyncMock)
@pytest.mark.parametrize(
    "mock_user_dependency, exp_id, exp_status, exp_json",
    [
        (
            "admin",
            1,
            status.HTTP_200_OK,
            ACTIVE_USER_EXP_JSON
        ),
        (
            "admin",
            404,
            status.HTTP_404_NOT_FOUND,
            {'detail': 'User not found'}
        ),
        (
            "active",
            1,
            status.HTTP_403_FORBIDDEN,
            {'detail': 'Access denied'}
        ),
    ],
    indirect=["mock_user_dependency"]
)
async def test_get_user(
        mock_get_user,
        client,
        mock_user_dependency,
        exp_id,
        exp_status,
        exp_json
):
    """
    Test getting user (admin required).
    """
    if exp_status == status.HTTP_200_OK:
        mock_get_user.return_value = ACTIVE_USER_EXP_JSON
    else:
        mock_get_user.return_value = None

    response = await client.get(f'/users/{exp_id}/')

    assert response.status_code == exp_status
    assert response.json() == exp_json

    mock_get_user.assert_called_once() if (
        response.status_code == status.HTTP_200_OK
    ) or (
        response.status_code == status.HTTP_404_NOT_FOUND
    ) else mock_get_user.assert_not_called()


@pytest.mark.asyncio
@patch("src.users.routes.UserCRUD.delete_user", new_callable=AsyncMock)
@pytest.mark.parametrize(
    "mock_user_dependency, exp_status, exp_json",
    [
        (
            "admin",
            status.HTTP_204_NO_CONTENT,
            None
        ),
        (
            "active",
            status.HTTP_403_FORBIDDEN,
            {'detail': 'Access denied'}
        ),
    ],
    indirect=["mock_user_dependency"]
)
async def test_delete_user(
        mock_delete_user,
        client,
        mock_user_dependency,
        exp_status,
        exp_json
):
    """
    Test delete user (admin required).
    """
    response = await client.delete('/users/1/')

    assert response.status_code == exp_status
    if exp_json:
        assert response.json() == exp_json

    mock_delete_user.assert_called_once() if (
        response.status_code == status.HTTP_204_NO_CONTENT
    ) else mock_delete_user.assert_not_called()


@pytest.mark.asyncio
@patch("src.users.routes.UserCRUD.update_user", new_callable=AsyncMock)
@pytest.mark.parametrize(
    "mock_user_dependency, user_id, input_data, exp_status, exp_json",
    [
        (
            "admin",
            3,
            {
                "username": "upd_username",
                "name": "upd_name",
                "email": "updated@mail.com"
            },
            status.HTTP_200_OK,
            {
                "username": "upd_username",
                "name": "upd_name",
                "email": "updated@mail.com"
            }
        ),
        (
            "admin",
            3,
            {},
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            {
                'detail': [
                    {
                        'input': None,
                        'loc': ['body'],
                        'msg': 'Field required',
                        'type': 'missing'
                    }
                ]
            }
        ),
        (
            "active",
            1,
            {
                "username": "upd_username",
                "name": "upd_name",
                "email": "updated@mail.com"
            },
            status.HTTP_200_OK,
            {
                "username": "upd_username",
                "name": "upd_name",
                "email": "updated@mail.com"
            },
        ),
        (
            "active",
            3,
            {"username": "test"},
            status.HTTP_403_FORBIDDEN,
            {'detail': 'Access denied'}
        ),
    ],
    indirect=["mock_user_dependency"]
)
async def test_user_update(
        mock_update_user,
        client,
        mock_user_dependency,
        user_id,
        input_data,
        exp_status,
        exp_json
):
    """
    Testing update user.
    """
    if exp_status == status.HTTP_403_FORBIDDEN:
        response_data = None
    else:
        response_data = {
            "username": "upd_username",
            "name": "upd_name",
            "email": "updated@mail.com"
        }
    mock_update_user.return_value = response_data

    response = await client.put(
        f'/users/{user_id}/',
        json=input_data if input_data else None
    )

    assert response.status_code == exp_status
    assert response.json() == exp_json


@pytest.mark.asyncio
@patch("src.users.routes.UserCRUD.get_user", new_callable=AsyncMock)
@pytest.mark.parametrize(
    "mock_user_dependency, user_id, input_data, exp_status, exp_json",
    [
        (
            "active",
            1,
            {
                "old_password": "valid_password",
                "new_password": "new_password"
            },
            status.HTTP_200_OK,
            {'detail': 'Password successfully updated!'}
        ),
        (
            "active",
            1,
            {
                "old_password": "wrong_password",
                "new_password": "new_password"
            },
            status.HTTP_403_FORBIDDEN,
            {'detail': 'Wrong password'}
        ),
        (
            "active",
            3,
            {
                "old_password": "valid_password",
                "new_password": "new_password"
            },
            status.HTTP_403_FORBIDDEN,
            {'detail': 'Access denied'}
        ),
        (
            "active",
            4,
            {
                "old_password": "valid_password",
                "new_password": "new_password"
            },
            status.HTTP_404_NOT_FOUND,
            {'detail': 'User not found'}
        ),
    ]
)
async def test_password_update(
        mock_get_user,
        client,
        mock_user_dependency,
        user_id,
        input_data,
        exp_status,
        exp_json
):
    """
    Testing update password.
    """
    if (exp_status == status.HTTP_200_OK) or (exp_status == status.HTTP_403_FORBIDDEN):
        user = User(
            id=1,
            email='valid@mail.com',
            name='valid',
            password=hash_password('valid_password'),
            username='valid_username',
            is_active=True,
            is_admin=False
        )
    else:
        user = None


    mock_get_user.return_value = user
    with patch(
            "src.users.routes.UserCRUD.update_user",
            new_callable=AsyncMock
    ) as mock_update_user:
        mock_update_user.return_value = None

        response = await client.put(
            f'/users/password/{user_id}/',
            json=input_data if input_data else None
        )

        assert response.status_code == exp_status
        assert response.json() == exp_json
