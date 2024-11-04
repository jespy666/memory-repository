import secrets

from typing import TypeVar, Sequence, Dict, Optional

from sqlalchemy import select, delete

from src.users.models import User
from src.users.schemas import UserSchema, UserUpdate

from src.session import AsyncSessionFactory, AsyncSession

from src.auth.schemas import UserCreate
from src.auth.utils import hash_password

from src import exceptions as exc


T = TypeVar('T', str, int, bool)
U = TypeVar('U', str, int, bool)


class UserCRUD(AsyncSessionFactory):

    async def get_all_users(self) -> Sequence[User]:
        """
        Retrieve all users from DB.

        Returns:
             Sequence of users or empty list.
        """
        session: AsyncSession = await super().get_session()
        stmt = select(User)
        response = await session.scalars(stmt)
        await session.close()
        return response.all()

    async def get_user(self, field: str, value: T) -> User:
        """
        Getting user from DB by any existing field.

        Args:
            field: Any existing field name.
            value: Field value to search.
        Returns:
             User obj or None.
        """
        session: AsyncSession = await super().get_session()
        if not hasattr(User, field):
            raise exc.NonExistedAttributeException

        # noinspection PyTypeChecker
        stmt = select(User).where(getattr(User, field) == value)
        response = await session.execute(stmt)
        user = response.scalar_one_or_none()
        await session.close()
        return user

    async def create_user(
            self,
            user_data: UserCreate,
            superuser: bool = False
    ) -> UserSchema:
        """
        Create new user.

        Args:
            user_data: All new user data.
            superuser (boolean): A flag represented to provide new user admin
            rights.
        Returns:
             User represented schema.
        """
        hashed_password: str = hash_password(user_data.password)
        user = User(
            email=user_data.email,
            password=hashed_password,
            name=user_data.name,
            is_admin=False if not superuser else True,
            is_active=False
        )

        # set username
        prefix = secrets.token_hex(2)
        username = f'{user.name}-{prefix}'
        user.username = username

        session: AsyncSession = await super().get_session()
        session.add(user)
        await session.commit()
        await session.refresh(user)
        await session.close()
        return UserSchema(
            email=user.email,
            password=user.password,
            name=user.name
        )

    async def delete_user(self, field: str, value: T) -> None:
        """
        Delete user by any users filed.

        Args:
            field: A user model field name.
            value: A user field value.
        """
        if not hasattr(User, field):
            raise exc.NonExistedAttributeException

        # noinspection PyTypeChecker
        stmt = delete(User).where(getattr(User, field) == value)
        session: AsyncSession = await super().get_session()
        await session.execute(stmt)
        await session.commit()
        await session.close()

    async def update_user(
            self,
            field: str,
            value: T,
            data: Dict[str, U]
    ) -> UserUpdate:
        """
        Update user.

        Args:
            field (string): Field to find user.
            value (string/integer): Value to find user.
            data (dictionary): Data to update user.
        Returns:
            User object.
        Raises:
            UserNotFoundException: If user not found by given value.
        """
        user: Optional[User] = await self.get_user(field, value)
        if not user:
            raise exc.UserNotFoundException

        session: AsyncSession = await super().get_session()
        try:
            for key, val in data.items():
                if hasattr(user, key) and val:
                    setattr(user, key, val)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return UserUpdate(
                email=user.email,
                name=user.name,
                username=user.username,
            )
        finally:
            await session.close()
