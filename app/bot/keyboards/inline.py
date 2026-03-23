from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from hashlib import md5

from app.storage.orders import save_order
from app.models.order import Order


def generate_order_id(order: Order) -> str:
    return md5(order.url.encode()).hexdigest()


def get_order_keyboard(order):
    order_id = generate_order_id(order)
    save_order(order_id, order)

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text='🧠 AI',
                callback_data=f'ai:{order_id}'
            ),
            InlineKeyboardButton(
                text='❌ Skip',
                callback_data=f'skip:{order_id}'
            )
        ],
        [
            InlineKeyboardButton(
                text='🔗 Открыть заказ',
                url=order.url
            )
        ]
    ])


def get_ai_keyboard(order: Order, order_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text='🔄 Переген',
                callback_data=f'ai:{order_id}:regen'
            ),
            InlineKeyboardButton(
                text='❌ Скип',
                callback_data=f'skip:{order_id}'
            )
        ],
        [
            InlineKeyboardButton(
                text='✅ Отправить',
                callback_data=f'send:{order_id}'
            )
        ],
        [
            InlineKeyboardButton(
                text='🔗 Открыть заказ',
                url=order.url
            )
        ]
    ])
