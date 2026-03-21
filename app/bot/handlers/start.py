from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import Router


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    text = """
    👋 Привет!
    
    Я бот для поиска заказов на Kwork.
    
    Что я умею:
    • нахожу новые заказы
    • фильтрую мусор
    • помогаю писать отклики
    
    Как пользоваться:
    1. Жди заказы
    2. Жми "🚀 Откликнуться"
    3. Получай готовый текст
    
    👇 Поехали!
    """

    await message.answer(text)
