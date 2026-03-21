from openai import AsyncOpenAI
from loguru import logger
from app.config.settings import OPENROUTER_API_KEY
from app.models.order import Order


class AIFilter:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url='https://openrouter.ai/api/v1',
            api_key=OPENROUTER_API_KEY,
        )
        self.model = 'deepseek/deepseek-chat'
        self.system_prompt = (
            "ЗАДАЧА: выбрать ТОЛЬКО максимально выгодные заказы.\n\n"

            "=== ГЛАВНЫЙ ПРИНЦИП ===\n"
            "Оценивай ВЫГОДУ = деньги / время / сложность.\n"
            "НЕ важно сколько платят — важно насколько это быстро и легко делается.\n\n"

            "YES — если это быстрые деньги.\n"
            "NO — если это долго, сложно или мутно.\n\n"

            "=== ИДЕАЛЬНЫЙ ЗАКАЗ ===\n"
            "Пример: 'сделать парсер за вечер за 10000'\n"
            "→ это идеальный YES\n\n"

            "=== ОЦЕНКА ВРЕМЕНИ ===\n"
            "YES если:\n"
            "- можно сделать за 1 вечер (1-5 часов) и платят >= 5000\n"
            "- можно сделать за 1 день и платят >= 7000\n"
            "- можно сделать за 2-3 дня и платят >= 10000\n\n"

            "NO если:\n"
            "- займет неделю или больше\n"
            "- требует долгой поддержки\n"
            "- непонятно сколько времени займет\n\n"

            "=== ЧТО ОБЫЧНО ВЫГОДНО ===\n"
            "- парсеры\n"
            "- боты\n"
            "- автоматизация\n"
            "- скрипты\n"
            "- API / интеграции\n\n"

            "=== ЧТО ОБЫЧНО НЕВЫГОДНО ===\n"
            "- большие проекты\n"
            "- доработка чужого проекта\n"
            "- поддержка\n"
            "- 'доработать', 'переделать'\n\n"

            "=== ЖЕСТКИЙ ОТСЕВ ===\n"
            "Всегда NO:\n"
            "- дизайн (баннеры, логотипы, креативы)\n"
            "- видео, монтаж\n"
            "- маркетинг, реклама\n"
            "- тексты, презентации\n"
            "- SEO\n"
            "- поиск клиентов\n\n"

            "=== ПЛОХИЕ СИГНАЛЫ ===\n"
            "NO если:\n"
            "- цена < 3000\n"
            "- откликов > 20\n"
            "- размытое описание\n\n"

            "=== ВАЖНО ===\n"
            "Если заказ простой и быстрый, но не идеально описан —\n"
            "лучше дать YES, чем пропустить выгодный заказ.\n\n"

            "=== ФОРМАТ ОТВЕТА ===\n"
            "Строго список:\n"
            "YES\n"
            "NO\n"
            "YES\n\n"

            "НИКАКИХ объяснений.\n"
            "Любой другой формат = ошибка.\n"
        )
        self.score_prompt = (
            "Ты опытный фрилансер-разработчик.\n"
            "Ты зарабатываешь на быстрых и простых задачах.\n\n"

            "У тебя есть ограничение: 1–3 отклика в день.\n"
            "Ты выбираешь ТОЛЬКО лучшие заказы.\n\n"

            "=== ТВОЯ СПЕЦИАЛИЗАЦИЯ ===\n"
            "Ты работаешь ТОЛЬКО с:\n"
            "- парсеры\n"
            "- telegram боты\n"
            "- python скрипты\n"
            "- автоматизация\n"
            "- API интеграции\n\n"

            "Если заказ НЕ относится к этим категориям → оценка не выше 3.\n\n"

            "=== ТВОЯ ЦЕЛЬ ===\n"
            "Максимум денег за минимум времени.\n\n"

            "=== КАК ДУМАТЬ ===\n"
            "Спроси себя:\n"
            "'Я бы потратил на это один из 3 откликов сегодня?'\n\n"

            "Если есть сомнения — снижай оценку.\n\n"

            "=== ХОРОШИЕ ЗАКАЗЫ ===\n"
            "- четкое ТЗ\n"
            "- можно сделать за 1-5 часов\n"
            "- цена от 5000+\n"
            "- мало откликов (<10)\n\n"

            "=== ПЛОХИЕ ЗАКАЗЫ ===\n"
            "- дизайн, видео, тексты, маркетинг\n"
            "- 'доработать', 'переделать'\n"
            "- непонятный объем\n"
            "- много откликов (>15)\n\n"

            "=== ШКАЛА ===\n"
            "10 = идеальный, беру сразу\n"
            "8-9 = очень хороший\n"
            "6-7 = сомнительно\n"
            "0-5 = не беру\n\n"

            "=== ВАЖНО ===\n"
            "Лучше пропустить, чем потратить отклик на слабый заказ.\n\n"

            "Ответь ТОЛЬКО числом от 0 до 10."
        )

    @staticmethod
    def build_prompt(orders: list[Order]) -> str:
        lines = []

        for i, o in enumerate(orders, 1):
            price = " - ".join(map(str, o.prices))

            lines.append(
                f"{i}. {o.title}\n"
                f"Цена: {price}\n"
                f"Отклики: {o.responses}\n"
                f"{o.description[:200]}"
            )

        return "\n\n".join(lines)

    async def check_order(self, order: Order) -> bool:
        prompt = (
            f"{order.title}\n"
            f"Цена: {' - '.join(map(str, order.prices))}\n"
            f"Отклики: {order.responses}\n"
            f"{order.description[:300]}"
        )

        logger.debug(f"AI SINGLE PROMPT:\n{prompt}")

        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ]

            response = await self.client.chat.completions.create(
                model=self.model,
                temperature=0,
                messages=messages  # type: ignore
            )

            content = response.choices[0].message.content.strip().upper()

            return "YES" in content

        except Exception as ex:
            logger.error(f"AI error (single): {ex}")
            return False

    async def score_order(self, order: Order) -> int:
        prompt = (
            f"{order.title}\n"
            f"Цена: {' - '.join(map(str, order.prices))}\n"
            f"Отклики: {order.responses}\n"
            f"{order.description[:300]}"
        )

        try:
            messages = [
                {"role": "system", "content": self.score_prompt},
                {"role": "user", "content": prompt},
            ]
            response = await self.client.chat.completions.create(
                model=self.model,
                temperature=0,
                messages=messages # type: ignore
            )

            content = response.choices[0].message.content.strip()

            return int(content)

        except Exception as e:
            logger.error(f"AI score error: {e}")
            return 0

    async def check_batch(self, orders: list[Order]) -> list[bool]:
        if not orders:
            return []

        prompt = self.build_prompt(orders)

        logger.debug(f"AI PROMPT:\n{prompt}")

        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ]
            response = await self.client.chat.completions.create(
                model=self.model,
                temperature=0,
                messages=messages # type: ignore
            )

            content = response.choices[0].message.content.strip()

            lines = content.split("\n")

            results = []
            for line in lines:
                results.append("YES" in line.upper())

            # защита если модель ответила криво
            if len(results) != len(orders):
                return [False] * len(orders)

            return results

        except Exception as ex:
            print(f"AI error: {ex}")
            return [False] * len(orders)
