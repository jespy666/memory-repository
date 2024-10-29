from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean

from src import Base


class User(Base):

    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=False,
        nullable=True
    )

    name: Mapped[str] = mapped_column(
        String(50),
        unique=False,
        nullable=False
    )

    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    password: Mapped[str] = mapped_column(
        String(128),
        unique=False,
        nullable=False
    )

    avatar: Mapped[str] = mapped_column(
        String,
        nullable=True,
        unique=False
    )

    def __str__(self):
        return self.username if self.username else self.name
