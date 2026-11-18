import asyncio

from app.event_bus import EventBus, History
from modules.cluster.core.entities.topic import TopicReset, TopicSpec
from modules.cluster.core.errors.cluster_errors import TopicAlreadyExistsError, TopicOperationError
from modules.cluster.core.interfaces.cluster_gateway import ClusterGateway


class ResetTopic:
    def __init__(
        self,
        gateway: ClusterGateway,
        topic: TopicSpec,
        event_bus: EventBus,
        recreate_timeout_seconds: float = 20.0,
        recreate_poll_seconds: float = 0.5,
    ) -> None:
        self._gateway = gateway
        self._topic = topic
        self._event_bus = event_bus
        self._recreate_timeout_seconds = recreate_timeout_seconds
        self._recreate_poll_seconds = recreate_poll_seconds

    async def execute(self) -> TopicReset:
        await self._gateway.delete_topic(self._topic.name)
        try:
            async with asyncio.timeout(self._recreate_timeout_seconds):
                await self._recreate_once_deleted()
        except TimeoutError as error:
            raise TopicOperationError(f"Topic {self._topic.name} could not be recreated in time") from error
        reset = TopicReset(self._topic.name, self._topic.partitions, self._topic.replication_factor)
        self._event_bus.publish(reset.event_type, reset, history=History.TIMELINE)
        return reset

    async def _recreate_once_deleted(self) -> None:
        while True:
            try:
                await self._gateway.create_topic(self._topic)
                return
            except TopicAlreadyExistsError:
                await asyncio.sleep(self._recreate_poll_seconds)
