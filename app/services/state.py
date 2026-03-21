from app.models.order import Order


FILE_PATH = '../data/last_order.txt'


def load_last_order() -> str:
    with open(FILE_PATH, 'r') as file:
        return file.read()


def save_last_order(order: Order):
    with open(FILE_PATH, 'w') as file:
        file.write(order.url)
