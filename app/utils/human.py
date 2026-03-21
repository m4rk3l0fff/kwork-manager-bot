from random import uniform
import asyncio


async def human_delay() -> None:
    await asyncio.sleep(uniform(2, 4))
