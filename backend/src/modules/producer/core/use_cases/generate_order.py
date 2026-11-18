import itertools
import random
from datetime import UTC, datetime

from modules.producer.core.entities.order import OrderCreated

PRODUCTS: tuple[tuple[str, float], ...] = (
    ("Mechanical Keyboard", 129.90),
    ("Wireless Mouse", 39.50),
    ("27-inch Monitor", 289.00),
    ("USB-C Hub", 49.99),
    ("Noise-Cancelling Headphones", 249.00),
    ("Laptop Stand", 59.00),
    ("Webcam 4K", 159.00),
    ("Portable SSD 1TB", 109.00),
)

REGIONS: tuple[tuple[str, str], ...] = (
    ("EU", "EUR"),
    ("AFRICA", "ZAR"),
    ("US", "USD"),
)


class OrderGenerator:
    def __init__(self, randomizer: random.Random | None = None, first_order_number: int = 10001) -> None:
        self._random = randomizer or random.Random()
        self._order_numbers = itertools.count(first_order_number)

    def next_order(self) -> OrderCreated:
        product, unit_price = self._random.choice(PRODUCTS)
        region, currency = self._random.choice(REGIONS)
        quantity = self._random.choices((1, 2, 3), weights=(7, 2, 1))[0]
        return OrderCreated(
            order_id=f"ORD-{next(self._order_numbers)}",
            product=product,
            quantity=quantity,
            amount=round(unit_price * quantity, 2),
            currency=currency,
            region=region,
            created_at=datetime.now(UTC),
        )
