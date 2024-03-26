from .objects import Events, Configs, Points

from sqlalchemy import select

async def add_event(cog, date, id, msgId):
    async with cog.session() as conn:
        result = await conn.execute(select(Events).where(Events.id == id))

        if result:
            result = result.scalars().first()
            result.duration = date
            result.messageId = msgId
        else:
            cog.session.add(Events(id=id, duration=date, messageId=msgId))
        await cog.session.commit()

async def fetch_config(cog, id) -> Configs:
    async with cog.session() as conn:
        result = await conn.execute(select(Configs).where(Configs.id == id))
        if result:
            return result.scalars().first()


async def add_config(cog, id, channel):
    async with cog.session() as conn:
        result = await conn.execute(select(Configs).where(Configs.id == id))

        if result:
            config = result.scalars().first()
            config.channel = channel
        else:
            cog.session.add(Configs(id=id, channel=channel))
        await cog.session.commit()


async def add_points(cog, id, userid, month, point):
    async with cog.session() as conn:
        result = await conn.execute(select(Points).where(Points.id == id))

        if result:
            points = result.scalars().first()
            points.point += point
        else:
            cog.session.add(Points(id=id, userid=userid, month=month, point=point))
        await cog.session.commit()
