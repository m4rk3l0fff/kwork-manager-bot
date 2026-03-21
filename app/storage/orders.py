ORDERS_CACHE = {}


def save_order(order_id: str, order):
    ORDERS_CACHE[order_id] = order


def get_order(order_id: str):
    return ORDERS_CACHE.get(order_id)
