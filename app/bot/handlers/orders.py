from aiogram.types import CallbackQuery
from aiogram import Router, F

from app.storage.orders import get_order
from app.bot.keyboards.inline import get_ai_keyboard
from app.services.response_generator import generate


router = Router()
generated_texts = {}


@router.callback_query(F.data.startswith('ai:'))
async def handle_ai(callback: CallbackQuery):
    await callback.answer()

    parts = callback.data.split(':')
    order_id = parts[1]
    mode = parts[2] if len(parts) > 2 else 'new'

    order = get_order(order_id)

    if not order:
        await callback.answer('Заказ не найден')
        return

    original_text = callback.message.text

    try:
        result = await generate(order)
        if not result:
            await callback.answer("Ошибка генерации", show_alert=True)
            return

        ai_text = f'<code>{result["text"]}</code>'
        price = result["price"]
        time_days = result["time_days"]

    except Exception:
        await callback.answer("Ошибка генерации", show_alert=True)
        return

    generated_texts[order_id] = ai_text

    if mode == 'regen':
        ai_block = (
            "\n\n"
            "🔄 Новый вариант:\n\n"
            f"{ai_text}\n\n"
            f"💰 {price} ₽ | ⏱ {time_days} дн.\n"
            "━━━━━━━━━━━━━━━"
        )
    else:
        ai_block = (
            "\n\n"
            "━━━━━━━━━━━━━━━\n"
            "🚀 Можно отправить так:\n\n"
            f"{ai_text}\n\n"
            f"💰 {price} ₽ | ⏱ {time_days} дн.\n"
            "━━━━━━━━━━━━━━━"
        )

    new_text = original_text + ai_block

    await callback.message.edit_text(
        new_text,
        reply_markup=get_ai_keyboard(order, order_id),
        parse_mode='HTML'
    )


@router.callback_query(F.data.startswith('send:'))
async def handle_send(callback: CallbackQuery):
    await callback.answer('Пока недоступно')

    # order_id = callback.data.split(':')[1]
    #
    # text = generated_texts.get(order_id)
    #
    # if not text:
    #     await callback.answer('Нет текста')
    #     return
    #
    # await callback.message.answer(text)
    # await callback.answer('Отправлено')


@router.callback_query(F.data.startswith('skip:'))
async def handle_skip(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer('Скрыто')
