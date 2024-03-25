# db
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from datetime import datetime

from typing import Optional

from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Points(Base):
    __tablename__ = "points"
    id: Mapped[int] = mapped_column(primary_key=True)
    month: Mapped[int]
    points: Mapped[int]


class Config(Base):
    __tablename__ = "config"
    guild_id: Mapped[int] = mapped_column(primary_key=True)
    sub_channel: Mapped[Optional[int]]


class Genres(Base):
    __tablename__ = "genres"
    id: Mapped[int] = mapped_column(primary_key=True)
    genre_name: Mapped[str]


class events(Base):
    __tablename__ = "events"
    id = Column(Integer, ForeignKey("Seasons.guild_id"))
    text: Mapped[str]
    time: Mapped[int]  # unix timestamp


class Seasons(Base):
    __tablename__ = "seasons"
    guild_id: Mapped[int] = mapped_column(primary_key=True)
    length: Mapped[int]
    points: Mapped[Points] = relationship()
