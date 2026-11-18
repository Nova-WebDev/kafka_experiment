from abc import ABC, abstractmethod

from modules.consumer.core.use_cases.demo_consumer import DemoConsumer


class ConsumerRegistry(ABC):
    @abstractmethod
    def next_id(self) -> str: ...

    @abstractmethod
    def add(self, consumer: DemoConsumer) -> None: ...

    @abstractmethod
    def get(self, consumer_id: str) -> DemoConsumer: ...

    @abstractmethod
    def remove(self, consumer_id: str) -> DemoConsumer: ...

    @abstractmethod
    def all(self) -> list[DemoConsumer]: ...
