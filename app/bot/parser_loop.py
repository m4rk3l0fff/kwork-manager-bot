from random import uniform
from loguru import logger
from traceback import format_exc
import asyncio

from app.services.state import load_last_order, save_last_order
from app.services.order_batcher import OrderBatcher
from app.services.order_filters import is_good_order
from app.services.ai_filter import AIFilter
from app.bot.sender import send_order


batcher = OrderBatcher()
ai_filter = AIFilter()


async def parser_loop(bot: Bot, parser: KworkParser) -> None:
    while True:
        try:
            orders = await parser.get_orders(stop_at=load_last_order())

            logger.success(f"📦 Получили {len(orders)} заказов")

            for order in reversed(orders):
                if not is_good_order(order):
                    logger.info(f'❌ Фильтр | {order.title[:40]}... | 💰 {max(order.prices)}')

                    continue

                score = await ai_filter.score_order(order)
                if score < 8:
                    logger.info(f'🚫 Скип | score={score} | {order.title[:40]}...')

                    continue

                logger.success(f'🔥 ВЗЯЛ | score={score}/10 | 💰 {max(order.prices)} | {order.title[:50]}...')

                await send_order(bot, order, score)
                await asyncio.sleep(1)

            if orders:
                save_last_order(orders[0])

        except Exception as ex:
            logger.error(f'Ошибка в parser_loop: {ex}')

        await asyncio.sleep(uniform(25, 45))
