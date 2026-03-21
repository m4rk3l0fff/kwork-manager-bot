from openai import OpenAI
import asyncio

from app.models.order import Order


class ResponseGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

        self.models = [
            "deepseek/deepseek-chat"
        ]

    async def generate(self, order: Order) -> str | None:
        prompt = self._build_prompt(order)

        for model in self.models:
            for _ in range(2):
                try:
                    response = await asyncio.to_thread(
                        self.client.chat.completions.create,
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                    )

                    text = response.choices[0].message.content.strip()

                    if self._is_valid(text):
                        return text

                except Exception:
                    await asyncio.sleep(2)

        return None

    @staticmethod
    def _is_valid(text: str) -> bool:
        if not text:
            return False

        # защита от слишком длинных ответов
        if len(text.splitlines()) > 8:
            return False

        # защита от "роботских" ответов
        bad_phrases = [
            "я лучший",
            "имею большой опыт",
            "готов выполнить",
            "обращайтесь",
        ]

        for phrase in bad_phrases:
            if phrase in text.lower():
                return False

        return True

    @staticmethod
    def _build_prompt(order: Order) -> str:
        return f"""
Ты — опытный фрилансер (Python, парсинг, автоматизация).

Напиши отклик так, чтобы заказчик выбрал тебя.

ПРАВИЛА:
- 3–6 строк
- без воды
- не как робот
- не используй шаблонные фразы

ОСНОВНОЕ:
- покажи, что понял задачу
- используй детали из описания
- предложи конкретное решение
- можно задать 1 короткий вопрос

СТИЛЬ:
живой, как в Telegram

ЗАКАЗ:
{order.title}
{order.description}
"""