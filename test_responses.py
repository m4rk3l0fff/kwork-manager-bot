from openai import AsyncOpenAI
import asyncio

from app.models.order import Order
from app.config.settings import OPENROUTER_API_KEY


client = AsyncOpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")
PROMPT = """
Ты фрилансер, который пишет отклики на заказы.

СТИЛЬ: {STYLE}

ЗАДАЧА:
Напиши отклик как живой человек с опытом, который сразу понял задачу.

СТРУКТУРА:
1. Суть решения
2. Конкретная деталь (где проблема или как решается)
3. Срок в часах

ТРЕБОВАНИЯ:
- 2-3 предложения
- простой разговорный язык
- уверенный тон (без пафоса)
- каждый отклик формулируется по-разному

ОБЯЗАТЕЛЬНО:
- 1 микро-деталь (дубли, логика, структура, обновление)

ЗАПРЕЩЕНО:
- "разработаю", "сделаю", "готов"
- "обратите внимание", "важно отметить"
- сложные технические термины
- писать как статья

ЦЕНА:
- строго по диапазонам:
  - парсинг товаров: 8000–12000
  - avito: 10000–15000
  - бот: 6000–10000
- брать среднее значение

ВРЕМЯ:
- текст: 10–14 часов
- time_days: 1–2

ФОРМАТ:
{
  "text": "...",
  "price": int,
  "time_days": int
}
"""

async def generate(order: Order):
    response = await client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[ # type: ignore
            {"role": "system", "content": PROMPT},
            {
                "role": "user",
                "content": f"""
        Название: {order.title}
        Описание: {order.description}
        Цена: {order.prices}
        Отклики: {order.responses}
        """
            }
        ],
        temperature=0.7
    )

    content = response.choices[0].message.content

    print(f'RAW:\n{content}')


async def main():
    orders = [
        Order(
            title="Парсинг товаров с сайта",
            description="""
Нужно спарсить товары с сайта (около 800 позиций).

Собрать:
- название
- цену
- ссылку
- изображение

Результат в Excel.
Важно чтобы можно было запускать повторно.
""",
            prices=(5000, 15000),
            responses=3,
            url="https://kwork.ru/test1"
        ),

        Order(
            title="Telegram бот для записи клиентов",
            description="""
Нужен бот для записи клиентов в салон.

Функции:
- выбор услуги
- выбор даты и времени
- уведомления

Желательно на aiogram.
""",
            prices=(3000, 10000),
            responses=8,
            url="https://kwork.ru/test2"
        ),

        Order(
            title="Парсинг объявлений Avito",
            description="""
Нужно собирать объявления с Avito по фильтрам.

Данные:
- заголовок
- цена
- ссылка

Сохранять в CSV.
""",
            prices=(7000, 20000),
            responses=2,
            url="https://kwork.ru/test3"
        ),
    ]

    tasks = [generate(order) for order in orders]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # for order, result in zip(orders, results):
    #     print(f"\n=== {order.title} ===")
    #
    #     if isinstance(result, Exception):
    #         print("ERROR:", result)
    #     else:
    #         print(result)


if __name__ == "__main__":
    asyncio.run(main())
