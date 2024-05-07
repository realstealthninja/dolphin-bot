from .objects import Events, Configs, Points, Season, Submission

from sqlalchemy import select, delete


async def add_event(cog, date, id, msgId):
    async with cog.session() as conn:
        result = await conn.execute(select(Events).where(Events.id == id))

        event = result.scalars().first()
        season = await fetch_season(cog, id)
        if not season:
            conn.add(Season(id=id, month=1))
            await conn.commit()
        season = await fetch_season(cog, id)

        if event and season:
            event.duration = date
            event.messageId = msgId
            season.month += 1
        else:
            conn.add(Events(id=id, duration=date, messageId=msgId))
            season.month += 1
        await conn.commit()


async def fetch_config(cog, id) -> Configs | None:
    async with cog.session() as conn:
        result = await conn.execute(select(Configs).where(Configs.id == id))
        result = result.scalars().first()
        if result:
            return result
        else:
            return None


async def fetch_event(cog, id) -> Events | None:
    async with cog.session() as conn:
        result = await conn.execute(select(Events).where(Events.id == id))
        result = result.scalars().first()
        if result:
            return result
        else:
            return None


async def delete_event(cog, id) -> Events | None:
    async with cog.session() as conn:
        await conn.execute(delete(Events).where(Events.id == id))
        await conn.commit()


async def add_config(cog, id, channel) -> None:
    async with cog.session() as conn:
        result = await conn.execute(select(Configs).where(Configs.id == id))

        config = result.scalars().first()
        if config:
            config.channel = channel
        else:
            conn.add(Configs(id=id, channel=channel))
        await conn.commit()


async def fetch_submissions(cog, id) -> list[Submission]:
    async with cog.session() as conn:
        result = await conn.execute(select(Submission).where(Submission.id == id))

        return result.scalars().all()


async def add_reaction(cog, messgid):
    async with cog.session() as conn:
        result = await conn.execute(
            select(Submission).where(Submission.messageId == messgid)
        )
        result: Submission = result.scalars().first()
        if result:
            result.reactions += 1
            print(f"\n\nreactions: { result.reactions }\n")
        await conn.commit()


async def remove_reaction(cog, messageId):
    async with cog.session() as conn:
        result = await conn.execute(
            select(Submission).where(Submission.messageId == messageId)
        )
        result: Submission = result.scalars().first()
        if result:
            result.reactions -= 1
        await conn.commit()


async def reset_submissions(cog, id) -> None:
    async with cog.session() as conn:
        await conn.execute(delete(Submission).where(Submission.id == id))
        await conn.commit()


async def add_submssion(cog, id, messageid, userid):
    async with cog.session() as conn:
        result = await conn.execute(
            select(Submission).where(Submission.userId == userid)
        )
        result = result.scalars().first()
        if result:
            result.messageId = messageid
        else:
            conn.add(Submission(id=id, messageId=messageid, userId=userid, reactions=0))
        await conn.commit()


async def add_points(cog, id, userid, month, point):
    async with cog.session() as conn:
        result = await conn.execute(select(Points).where(Points.id == id))

        points = result.scalars().first()
        if points:
            points.point += point
        else:
            conn.add(Points(id=id, userid=userid, month=month, point=point))
        await conn.commit()


async def fetch_points(cog, id):
    async with cog.session() as conn:
        res = await conn.execute(select(Points).where(Points.id == id))
        return res.scalars().all()


async def fetch_season(cog, id) -> Season | None:
    async with cog.session() as conn:
        res = await conn.execute(select(Season).where(Season.id == id))
        return res.scalars().first()


async def make_leaderboard():
    pass
