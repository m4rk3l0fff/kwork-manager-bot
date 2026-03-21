from dataclasses import dataclass


@dataclass
class Order:
    title: str
    description: str
    prices: tuple[int, ...]
    responses: int
    url: str
