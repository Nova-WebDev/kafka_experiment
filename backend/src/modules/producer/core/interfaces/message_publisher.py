from abc import ABC, abstractmethod

from modules.producer.core.entities.message import DeliveryReceipt, OutgoingMessage


class MessagePublisher(ABC):
    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    async def stop(self) -> None: ...

    @abstractmethod
    async def send(self, message: OutgoingMessage) -> DeliveryReceipt: ...
