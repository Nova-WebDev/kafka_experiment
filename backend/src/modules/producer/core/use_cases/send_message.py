import time

from app.event_bus import EventBus, History
from modules.producer.core.entities.message import (
    MessageFailed,
    MessageSent,
    OutgoingMessage,
    SendOutcome,
    SendSource,
)
from modules.producer.core.errors.producer_errors import MessageDeliveryError
from modules.producer.core.interfaces.message_publisher import MessagePublisher


class SendMessage:
    def __init__(self, publisher: MessagePublisher, event_bus: EventBus) -> None:
        self._publisher = publisher
        self._event_bus = event_bus

    async def execute(self, message: OutgoingMessage, source: SendSource) -> SendOutcome:
        started = time.perf_counter()
        try:
            receipt = await self._publisher.send(message)
        except MessageDeliveryError as error:
            outcome: SendOutcome = MessageFailed(
                source=source,
                key=message.key,
                value=message.value,
                error=error.error_name,
                latency_ms=_elapsed_ms(started),
            )
        else:
            outcome = MessageSent(
                source=source,
                key=message.key,
                value=message.value,
                partition=receipt.partition,
                offset=receipt.offset,
                latency_ms=_elapsed_ms(started),
            )
        self._event_bus.publish(outcome.event_type, outcome, history=History.PRODUCER)
        return outcome


def _elapsed_ms(started: float) -> float:
    return round((time.perf_counter() - started) * 1000, 1)
