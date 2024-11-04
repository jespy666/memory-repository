from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine
)

from src.config import settings
from src.config.settings import Settings


class AsyncSessionFactory:

    conf: Settings = settings

    def __init__(self) -> None:
        self.db_url: str = self.conf.psql_url
        self.engine: AsyncEngine = create_async_engine(self.db_url)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autocommit=False,
            expire_on_commit=False,
        )

    async def get_session(self) -> AsyncSession:
        async with self.session_factory() as session:
            return session
