import time
from app.models.order import Order


class OrderBatcher:
    def __init__(self):
        self.buffer: list[Order] = []
        self.last_add_time: float | None = None

    def add(self, order: Order) -> None:
        self.buffer.append(order)
        self.last_add_time = time.time()

    def should_process(self) -> bool:
        if not self.buffer:
            return False

        # если накопили 3 заказа → сразу
        if len(self.buffer) >= 3:
            return True

        # если прошло 5 минут с последнего заказа
        if self.last_add_time and time.time() - self.last_add_time > 300:
            return True

        return False

    def pop_batch(self) -> list[Order]:
        batch = self.buffer.copy()
        self.buffer.clear()
        self.last_add_time = None
        return batch

    def get_batch(self):
        return self.buffer
