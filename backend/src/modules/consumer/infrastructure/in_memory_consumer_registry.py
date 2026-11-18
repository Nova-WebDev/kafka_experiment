import itertools
import string

from modules.consumer.core.errors.consumer_errors import ConsumerNotFoundError
from modules.consumer.core.interfaces.consumer_registry import ConsumerRegistry
from modules.consumer.core.use_cases.demo_consumer import DemoConsumer


class InMemoryConsumerRegistry(ConsumerRegistry):
    def __init__(self) -> None:
        self._consumers: dict[str, DemoConsumer] = {}
        self._sequence = itertools.count()

    def next_id(self) -> str:
        if not self._consumers:
            self._sequence = itertools.count()
        return _letters_for(next(self._sequence))

    def add(self, consumer: DemoConsumer) -> None:
        self._consumers[consumer.consumer_id] = consumer

    def get(self, consumer_id: str) -> DemoConsumer:
        try:
            return self._consumers[consumer_id]
        except KeyError as error:
            raise ConsumerNotFoundError(consumer_id) from error

    def remove(self, consumer_id: str) -> DemoConsumer:
        consumer = self.get(consumer_id)
        del self._consumers[consumer_id]
        return consumer

    def all(self) -> list[DemoConsumer]:
        return list(self._consumers.values())


def _letters_for(index: int) -> str:
    alphabet = string.ascii_uppercase
    letters = ""
    index += 1
    while index > 0:
        index, remainder = divmod(index - 1, len(alphabet))
        letters = alphabet[remainder] + letters
    return letters
