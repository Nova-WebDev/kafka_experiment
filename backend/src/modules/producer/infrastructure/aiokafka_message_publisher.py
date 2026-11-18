import asyncio

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from modules.producer.core.entities.message import DeliveryReceipt, OutgoingMessage
from modules.producer.core.errors.producer_errors import MessageDeliveryError, ProducerNotConnectedError
from modules.producer.core.interfaces.message_publisher import MessagePublisher

SEND_DEADLINE_MARGIN_SECONDS = 2.0


class AiokafkaMessagePublisher(MessagePublisher):
    def __init__(self, bootstrap_servers: list[str], topic: str, request_timeout_ms: int) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._topic = topic
        self._request_timeout_ms = request_timeout_ms
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        await self.stop()
        producer = AIOKafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
            client_id="kafka-lab-producer",
            acks="all",
            request_timeout_ms=self._request_timeout_ms,
            linger_ms=0,
        )
        try:
            await producer.start()
        except BaseException:
            await producer.stop()
            raise
        self._producer = producer

    async def stop(self) -> None:
        producer, self._producer = self._producer, None
        if producer is not None:
            await producer.stop()

    async def send(self, message: OutgoingMessage) -> DeliveryReceipt:
        if self._producer is None:
            raise ProducerNotConnectedError()
        deadline_seconds = self._request_timeout_ms / 1000 + SEND_DEADLINE_MARGIN_SECONDS
        try:
            async with asyncio.timeout(deadline_seconds):
                metadata = await self._producer.send_and_wait(
                    self._topic,
                    value=message.value.encode(),
                    key=message.key.encode() if message.key else None,
                )
        except TimeoutError as error:
            raise MessageDeliveryError("DeliveryTimeout") from error
        except KafkaError as error:
            raise MessageDeliveryError(_kafka_error_name(error)) from error
        return DeliveryReceipt(partition=metadata.partition, offset=metadata.offset)


def _kafka_error_name(error: KafkaError) -> str:
    return type(error).__name__.removesuffix("Error")
