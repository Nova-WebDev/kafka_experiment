import json
from dataclasses import dataclass
from datetime import datetime

from modules.producer.core.entities.message import OutgoingMessage


@dataclass(frozen=True)
class OrderCreated:
    order_id: str
    product: str
    quantity: int
    amount: float
    currency: str
    region: str
    created_at: datetime

    def to_message(self) -> OutgoingMessage:
        value = {
            "type": "OrderCreated",
            "orderId": self.order_id,
            "product": self.product,
            "quantity": self.quantity,
            "amount": self.amount,
            "currency": self.currency,
            "region": self.region,
            "createdAt": self.created_at.isoformat(timespec="seconds"),
        }
        return OutgoingMessage(key=self.region, value=json.dumps(value))
