from typing import List
from datetime import date
from sqlalchemy import ForeignKey   
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
        Mapped,
        DeclarativeBase,
        mapped_column,
        relationship
)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Season(Base):
    __tablename__ = "seasons"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    start_date: Mapped[date]
    end_date: Mapped[date]
    events: Mapped[List["Event"]] = relationship(back_populates="season")

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str | None]
    description: Mapped[str | None]

    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"))
    start_date: Mapped[date]
    end_date: Mapped[date]

    season: Mapped[Season] = relationship(back_populates="events")
    submissions: Mapped[List["Submission"]] = relationship(back_populates="event")
    samples: Mapped[List["Sample"]] = relationship(back_populates="event")


class Sample(Base):
    __tablename__ = "samples"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    name: Mapped[str | None]
    file: Mapped[bytes]

    event: Mapped[Event] = relationship(back_populates="samples") 

class Producer(Base):
    __tablename__ = "producers"
    id: Mapped[int] = mapped_column(primary_key=True)
    points: Mapped[int] = mapped_column(default=0)
    wins: Mapped[int] = mapped_column(default=0)
    
    submissions: Mapped[List["Submission"]] = relationship(back_populates="producer")


class Song(Base):
    __tablename__ = "songs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sub_id: Mapped[int] = mapped_column(ForeignKey("submissions.id"))
    name: Mapped[str | None]
    file: Mapped[bytes | None]

    submission: Mapped["Submission"] = relationship(back_populates="song")


class Submission(Base):
    __tablename__ = "submissions"
    id: Mapped[int] = mapped_column(primary_key=True)
    producer_id: Mapped[int] = mapped_column(ForeignKey("producers.id"))
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))

    reactions: Mapped[List["Reaction"]] = relationship(back_populates="submission")
    event: Mapped[Event] = relationship(back_populates="submissions")
    producer: Mapped[Producer] = relationship(back_populates="submissions")

    song: Mapped["Song"] = relationship(back_populates="submission")


class Reaction(Base):
    __tablename__ = "reactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id"))

    submission: Mapped[Submission] = relationship(back_populates="reactions")


