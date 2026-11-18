from modules.consumer.core.entities.commands import ConsumerCommand
from modules.consumer.core.interfaces.consumer_registry import ConsumerRegistry


class CommandConsumer:
    def __init__(self, registry: ConsumerRegistry) -> None:
        self._registry = registry

    def execute(self, consumer_id: str, command: ConsumerCommand) -> None:
        self._registry.get(consumer_id).submit(command)
