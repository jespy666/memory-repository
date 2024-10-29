from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    declared_attr
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy import func

from datetime import datetime


class Base(DeclarativeBase):

    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        unique=False,
        server_default=func.now(),
    )
