from modules.consumer.core.entities.consumer_overview import ConsumerOverview
from modules.consumer.core.interfaces.consumer_registry import ConsumerRegistry


class ListConsumers:
    def __init__(self, registry: ConsumerRegistry) -> None:
        self._registry = registry

    def execute(self) -> list[ConsumerOverview]:
        return [
            ConsumerOverview(state=consumer.state(), recent_messages=tuple(consumer.recent_messages()))
            for consumer in self._registry.all()
        ]
