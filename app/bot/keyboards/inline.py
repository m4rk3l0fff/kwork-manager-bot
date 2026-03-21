from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from hashlib import md5

from app.storage.orders import save_order
from app.models.order import Order


def get_order_keyboard(order: Order) -> InlineKeyboardMarkup:
    order_id = md5(order.url.encode()).hexdigest()
    save_order(order_id, order)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔥 Откликнуться",
                    callback_data=f"reply:{order_id}"
                ),
                InlineKeyboardButton(
                    text="🧠 AI",
                    callback_data=f"ai:{order_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❌ Скип",
                    callback_data=f"skip:{order_id}"
                ),
                InlineKeyboardButton(
                    text="🔗 Открыть",
                    url=order.url
                ),
            ]
        ]
    )