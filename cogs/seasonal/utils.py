from .objects import Events, Configs, Points

from sqlalchemy.orm import Select


async def add_event(session, date, id, msgId):
    async with session as conn:
        result = await conn.execute(Select(Events).where(Events.id == id))

        if result:
            result = result.scalars().one()
            result.duration = date
            result.messageId = msgId
        else:
            session.add(Events(id=id, duration=date, messageId=msgId))
        await session.commit()


async def add_config(session, id, channel):
    async with session as conn:
        result = await conn.execute(Select(Configs).where(Configs.id == id))

        if result:
            config = result.scalars().one()
            config.channel = channel
        else:
            session.add(Configs(id=id, channel=channel))
        await session.commit()


async def add_points(session, id, userid, month, point):
    async with session as conn:
        result = await conn.execute(Select(Points).where(Points.id == id))

        if result:
            points = result.scalars().one()
            points.point += point
        else:
            session.add(Points(id=id, userid=userid, month=month, point=point))
        await session.commit()
