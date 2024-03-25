from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Points(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    userid: Mapped[int]
    month: Mapped[int]
    point: Mapped[int]


class Configs(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    channel: Mapped[int]


class Events(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    duration: Mapped[int]
    messageId: Mapped[int]
