from aiogram import Bot

from app.bot.keyboards.inline import get_order_keyboard
from app.config.settings import CHAT_ID
from app.models.order import Order


async def send_order(bot: Bot, order: Order, result: dict):
    score = result.get("score", 0)
    complexity = result.get("complexity", 0)
    time_hours = result.get("time_hours", 0)

    text = (
        f"🔥 {order.title}\n\n"
        f"💰 {' - '.join(map(str, order.prices))}\n"
        f"⭐ Оценка: {score}/10\n"
        f"⚙️ Сложность: {complexity}/10\n"
        f"⏱ Время: {time_hours}ч\n"
        f"📩 Отклики: {order.responses}\n\n"
        f"{order.description[:200]}"
    )

    await bot.send_message(
        chat_id=CHAT_ID,
        text=text,
        reply_markup=get_order_keyboard(order)
    )
