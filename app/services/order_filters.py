from re import sub

from app.models.order import Order


EXCLUDE_KEYWORDS = [
    # 🎨 дизайн (максимально широко)
    "дизайн", "дизайнер", "обложк", "баннер", "логотип",
    "иллюстрац", "креатив", "оформлен", "ui", "ux", "figma",
    "photoshop", "фотошоп",

    # 📝 тексты
    "копирайт", "рерайт", "перевод", "написать текст",
    "статья", "контент", "описание товара",

    # 📢 маркетинг
    "таргет", "реклама", "маркетолог", "seo", "smm",
    "лиды", "лидогенерация", "продвижение",

    # 🧹 мусор
    "перепечат", "ввод текста", "заполнить таблиц",
    "без опыта", "легкий заработок", "школьник",

    # 🎬 медиа
    "монтаж", "озвучк", "видео", "рилс", "тикток",

    # ⚠️ опасные формулировки
    "доработать", "переделать", "исправить",

    "seo", "таргет", "реклама", "appsheet", "tilda", "битрикс", "дизайн"
]


def normalize(text: str) -> str:
    return sub(r"\s+", " ", text.lower()).strip()


def price_filter(order: Order, min_price: int = 3000, max_price: int = 50_000) -> bool:
    if not order.prices:
        return False

    return min(order.prices) >= min_price and max(order.prices) <= max_price


def response_filter(order: Order, max_responses: int = 15) -> bool:
    return order.responses < max_responses


def keyword_filter(order: Order) -> bool:
    text = normalize(order.title + " " + order.description)
    if any(word in text for word in EXCLUDE_KEYWORDS):
        return False

    return True


def is_good_order(order: Order) -> bool:
    if not price_filter(order):
        return False

    if not response_filter(order):
        return False

    if not keyword_filter(order):
        return False

    return True
