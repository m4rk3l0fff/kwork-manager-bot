from aiogram.types import CallbackQuery
from aiogram import Router, F

from app.storage.orders import get_order


router = Router()


@router.callback_query(F.data.startswith('reply:'))
async def handle_reply(callback: CallbackQuery):
    await callback.answer('Пока недоступно')

    # order_id = callback.data.split(':')[1]
    # order = get_order(order_id)
    #
    # text = f"""
    # Здравствуйте!
    #
    # Готов выполнить ваш заказ.
    # Есть опыт в подобных задачах.
    #
    # Вот ссылка на заказ:
    # {order.url}
    # """
    #
    # await callback.message.answer(text)


@router.callback_query(F.data.startswith('ai:'))
async def handle_reply(callback: CallbackQuery):
    await callback.answer('Пока недоступно')


@router.callback_query(F.data.startswith('skip:'))
async def handle_skip(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer('Скрыто')
    