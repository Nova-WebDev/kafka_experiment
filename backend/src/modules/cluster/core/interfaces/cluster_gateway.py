from abc import ABC, abstractmethod

from modules.cluster.core.entities.cluster_metadata import ClusterMetadata
from modules.cluster.core.entities.topic import TopicSpec


class ClusterGateway(ABC):
    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    async def fetch_metadata(self, topic: str) -> ClusterMetadata: ...

    @abstractmethod
    async def topic_exists(self, topic: str) -> bool: ...

    @abstractmethod
    async def create_topic(self, spec: TopicSpec) -> None: ...

    @abstractmethod
    async def delete_topic(self, topic: str) -> None: ...
