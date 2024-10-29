from typing import Optional

from sqlalchemy import select
from fastapi import HTTPException, status

from src.session import AsyncSessionFactory, AsyncSession
from src.users.models import User


class AuthCRUD(AsyncSessionFactory):

    async def activate_user(self, email: str) -> None:
        """
        Make user active.

        Args:
            email (string): Unique user email.
        """
        session: AsyncSession = await super().get_session()
        stmt = select(User).where(User.email == email)
        response = await session.execute(stmt)
        user: Optional[User] = response.scalar_one_or_none()
        if not user:
            await session.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )
        user.is_active = True
        await session.commit()
        await session.close()