from aiogram.types import CallbackQuery
from aiogram import Router, F

from app.storage.orders import get_order
from app.bot.keyboards.inline import get_ai_keyboard


router = Router()
generated_texts = {}


@router.callback_query(F.data.startswith('ai:'))
async def handle_ai(callback: CallbackQuery):
    order_id = callback.data.split(':')[1]
    order = get_order(order_id)

    if not order:
        await callback.message.edit_text('Заказ не найден')

        return

    text = (
        "Здравствуйте!\n\n"
        "Я внимательно изучил ваш заказ.\n"
        "Могу предложить решение под вашу задачу.\n"
        "Готов обсудить детали.\n\n"
        f"{order.url}"
    )

    generated_texts[order_id] = text

    await callback.message.edit_text(
        text + "\n\n---\n🤖 AI ответ:\n" + ai_text,
        reply_markup=get_ai_keyboard(order_id)
    )

    await callback.answer()


@router.callback_query(F.data.startswith('send:'))
async def handle_send(callback: CallbackQuery):
    order_id = callback.data.split(':')[1]

    text = generated_texts.get(order_id)

    if not text:
        await callback.answer('Нет текста')
        return

    await callback.message.answer(text)
    await callback.answer('Отправлено')


@router.callback_query(F.data.startswith('skip:'))
async def handle_skip(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer('Скрыто')
