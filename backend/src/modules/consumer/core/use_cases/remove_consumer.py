from app.event_bus import EventBus, History
from modules.consumer.core.entities.consumer_events import ConsumerRemoved
from modules.consumer.core.interfaces.consumer_registry import ConsumerRegistry


class RemoveConsumer:
    def __init__(self, registry: ConsumerRegistry, event_bus: EventBus) -> None:
        self._registry = registry
        self._event_bus = event_bus

    async def execute(self, consumer_id: str) -> None:
        consumer = self._registry.remove(consumer_id)
        await consumer.stop()
        removed = ConsumerRemoved(consumer_id=consumer.consumer_id, group_id=consumer.group_id)
        self._event_bus.publish(removed.event_type, removed, history=History.TIMELINE)

    async def execute_for_all(self) -> int:
        consumers = self._registry.all()
        for consumer in consumers:
            await self.execute(consumer.consumer_id)
        return len(consumers)
