from .objects import Events, Configs, Points, Season, Submission

from sqlalchemy import select, delete

import disnake


import cv2 as cv
import numpy as np


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


async def make_leaderboard(users: list[disnake.User], points: list[Points]):
    img = cv.imread("assets/images/leaderboard.png")

    for count, user in enumerate(users):
        avatar = await user.avatar.with_size(128).read()
        avatar = np.asarray(bytearray(avatar))
        avatar = cv.imdecode(avatar, cv.IMREAD_COLOR)

        img[50:50+128, 50+(160*count):50+128] = avatar

        color = (24, 91, 66)

        match count:
            case 0:
                color = (0, 255, 255)
            case 1:
                color = (255, 255, 255)
            case 2:
                color = (0, 123, 255)

        # #1
        cv.putText(img, f"#{count+1}", (195, 120+ (140 * count)), cv.FONT_HERSHEY_COMPLEX, 1, color, 2, cv.LINE_AA)
        # name
        cv.putText(img, user.name, (250, 120+ (140 * count)), cv.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2, cv.LINE_AA)
        # points
        cv.putText(img, f"⬤ {points[count].point}", (475, 120+ (140 * count)), cv.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2, cv.LINE_AA)
    
    cv.imwrite("board.png", img)
