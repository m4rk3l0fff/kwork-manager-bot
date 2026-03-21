from random import uniform
from loguru import logger
import asyncio
from aiogram import Bot

from app.services.state import load_last_order, save_last_order
from app.services.order_filters import is_good_order
from app.services.ai_filter import AIFilter
from app.bot.sender import send_order
from app.parsers.kwork_parser import KworkParser


ai_filter = AIFilter()


async def parser_loop(bot: Bot, parser: KworkParser) -> None:
    while True:
        try:
            orders = await parser.get_orders(stop_at=load_last_order())

            if not orders:
                await asyncio.sleep(uniform(25, 45))

                continue

            logger.info(f'ORDERS | count={len(orders)}')

            filtered_orders = [order for order in reversed(orders) if is_good_order(order)]

            if not filtered_orders:
                save_last_order(orders[0])

                await asyncio.sleep(uniform(25, 45))

                continue

            results = await ai_filter.analyze_batch(filtered_orders)

            good_count = sum(1 for result in results if result and result.get('score', 0) >= 8)
            logger.info(f'AI_BATCH | orders={len(results)} | good={good_count}')

            for order, result in zip(filtered_orders, results):

                if not result or 'score' not in result:
                    continue

                score = result.get('score')
                if score < 8:
                    continue

                logger.success(
                    f"🔥 TARGET | "
                    f"⭐ {score}/10 | "
                    f"⚙️ {result.get('complexity')}/10 | "
                    f"⏱ {result.get('time_hours')}h | "
                    f"💰 {max(order.prices)} | "
                    f"{order.title[:50]}"
                )

                await send_order(bot, order, result)
                await asyncio.sleep(1)

            save_last_order(orders[0])

        except Exception as ex:
            logger.error(f'PARSER_ERROR | {ex}')

        await asyncio.sleep(uniform(25, 45))
