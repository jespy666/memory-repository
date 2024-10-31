import pytest_asyncio

from httpx import AsyncClient

from src.app import app


@pytest_asyncio.fixture(scope='session')
async def client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
