from json import loads
from openai import AsyncOpenAI
from loguru import logger
from re import findall, DOTALL

from app.config.settings import OPENROUTER_API_KEY
from app.models.order import Order


class AIFilter:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url='https://openrouter.ai/api/v1',
            api_key=OPENROUTER_API_KEY,
        )
        self.model = 'deepseek/deepseek-chat'

        self.score_prompt = """
        Ты оцениваешь заказы как опытный фрилансер-разработчик (боты, парсинг, backend, автоматизация).
        
        Главная задача — поставить ОЦЕНКУ заказу (score от 1 до 10).
        
        Где:
        - 10 = идеально, стоит брать
        - 1 = мусор, не брать
        
        Оцени по:
        - смыслу задачи
        - сложности
        - времени выполнения
        - адекватности
        - срочности
        
        НЕ учитывай:
        - цену
        - отклики
        
        ---
        
        ПРАВИЛА:
        
        1. Если задача НЕ связана с IT (код, разработка, автоматизация) → score <= 3
        
        2. Если задача связана с:
        - докладами
        - рефератами
        - текстами
        - медициной
        → score <= 2
        
        3. Если есть слова:
        "срочно", "сегодня", "до завтра"
        → понижай score
        
        4. Если задача мутная, непонятная или плохо описана
        → score <= 4
        
        5. Не завышай оценки:
        - хорошие заказы редкость
        - большинство заказов — слабые
        
        ---
        
        Пример:
        
        Задача: "Сделать доклад по стоматологии до завтра"
        
        Ответ:
        {
          "score": 1,
          "complexity": 6,
          "time_hours": 10
        }
        
        ---
        
        Верни ТОЛЬКО валидный JSON  
        Без текста, без ```json, без объяснений
        
        Строго:
        
        {
          "score": число от 1 до 10,
          "complexity": число от 1 до 10,
          "time_hours": число
        }
        """

    @staticmethod
    def build_prompt(orders: list[Order]) -> str:
        lines = []

        for i, o in enumerate(orders, 1):
            price = ' - '.join(map(str, o.prices))

            lines.append(
                f'{i}. {o.title}\n'
                f'Цена: {price}\n'
                f'Отклики: {o.responses}\n'
                f'{o.description[:300]}'
            )

        return '\n\n'.join(lines)

    async def analyze_batch(self, orders: list[Order]) -> list[dict]:
        if not orders:
            return []

        prompt = self.build_prompt(orders)

        logger.debug(f'AI PROMPT:\n{prompt}')

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                temperature=0,
                messages=[ # type: ignore
                    {'role': 'system', 'content': self.score_prompt},
                    {'role': 'user', 'content': prompt}
                ]
            )

            content = response.choices[0].message.content

            if not content:
                logger.error('AI вернул пустой ответ')
                return []

            data = self.parse_ai_response(content)
            if not data:
                logger.error(f'AI вернул не JSON: {content}')
                return []

            return data

        except Exception as ex:
            logger.error(f'AI error: {ex}')
            return [{'worth_it': False}] * len(orders)

    @staticmethod
    def parse_ai_response(text: str) -> list[dict]:
        objects = findall(r"\{.*?\}", text, DOTALL)
        results = []

        for obj in objects:
            try:
                results.append(json.loads(obj))
            except:
                results.append(None)

        return results
