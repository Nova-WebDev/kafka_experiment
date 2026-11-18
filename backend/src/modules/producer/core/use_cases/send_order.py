from modules.producer.core.entities.message import SendOutcome, SendSource
from modules.producer.core.use_cases.generate_order import OrderGenerator
from modules.producer.core.use_cases.send_message import SendMessage


class SendOrder:
    def __init__(self, send_message: SendMessage, generator: OrderGenerator) -> None:
        self._send_message = send_message
        self._generator = generator

    async def execute(self, source: SendSource) -> SendOutcome:
        return await self._send_message.execute(self._generator.next_order().to_message(), source)
