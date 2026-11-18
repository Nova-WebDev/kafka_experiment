from pydantic import BaseModel

from modules.cluster.core.entities.topic import TopicReset


class TopicResetResponse(BaseModel):
    topic: str
    partitions: int
    replication_factor: int

    @classmethod
    def of(cls, reset: TopicReset) -> "TopicResetResponse":
        return cls(topic=reset.topic, partitions=reset.partitions, replication_factor=reset.replication_factor)
