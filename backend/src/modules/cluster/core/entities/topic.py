from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class TopicSpec:
    name: str
    partitions: int
    replication_factor: int
    min_insync_replicas: int


@dataclass(frozen=True)
class TopicReset:
    event_type: ClassVar[str] = "topic.reset"

    topic: str
    partitions: int
    replication_factor: int
