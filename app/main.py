import asyncio
from aiogram import Bot, Dispatcher

from app.services.browser import Browser
from app.parsers.kwork_parser import KworkParser
from app.bot.parser_loop import parser_loop
from app.config.settings import TOKEN
from app.utils.logger import setup_logger
from app.bot.handlers import routers


async def main() -> None:
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    for router in routers:
        dp.include_router(router)

    browser = Browser()
    await browser.start()

    parser = KworkParser(browser.page)

    asyncio.create_task(parser_loop(bot, parser))

    logger = setup_logger()
    logger.info("🚀 Бот запущен")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
