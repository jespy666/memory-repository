import pytest_asyncio

from httpx import AsyncClient

from src.depends import get_current_user
from src.users.models import User

from src.app import app


@pytest_asyncio.fixture(scope='session')
async def client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def mock_user_dependency(request):
    """
    Fixture overrides the get_current_user dependency based on the parameter.
    """
    if request.param == "active":
        app.dependency_overrides[get_current_user] = lambda: User(
            id=1,
            email='valid@mail.com',
            name='valid',
            password='valid_password',
            username='valid_username',
            is_active=True,
            is_admin=False
        )
    elif request.param == "not_active":
        app.dependency_overrides[get_current_user] = lambda: User(
            id=2,
            email='valid@mail.com',
            name='valid',
            password='valid_password',
            username='valid_username',
            is_active=False,
            is_admin=False
        )
    elif request.param == "admin":
        app.dependency_overrides[get_current_user] = lambda: User(
            id=3,
            email='admin@mail.com',
            name='admin',
            password='valid_password',
            username='admin',
            is_active=True,
            is_admin=True
        )
    yield
    app.dependency_overrides.pop(get_current_user)
