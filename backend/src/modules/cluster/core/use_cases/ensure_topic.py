from modules.cluster.core.entities.topic import TopicSpec
from modules.cluster.core.errors.cluster_errors import TopicAlreadyExistsError
from modules.cluster.core.interfaces.cluster_gateway import ClusterGateway


class EnsureTopic:
    def __init__(self, gateway: ClusterGateway, topic: TopicSpec) -> None:
        self._gateway = gateway
        self._topic = topic

    async def execute(self) -> None:
        if await self._gateway.topic_exists(self._topic.name):
            return
        try:
            await self._gateway.create_topic(self._topic)
        except TopicAlreadyExistsError:
            return
