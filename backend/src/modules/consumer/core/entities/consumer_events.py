from dataclasses import dataclass
from typing import ClassVar

from modules.consumer.core.entities.consumer_state import ConsumerState, PartitionProgress


@dataclass(frozen=True)
class ConsumerCreated:
    event_type: ClassVar[str] = "consumer.created"

    consumer_id: str
    group_id: str
    joined_existing_group: bool
    state: ConsumerState


@dataclass(frozen=True)
class ConsumerRemoved:
    event_type: ClassVar[str] = "consumer.removed"

    consumer_id: str
    group_id: str


@dataclass(frozen=True)
class ConsumerRebalanced:
    event_type: ClassVar[str] = "consumer.rebalanced"

    consumer_id: str
    group_id: str
    previous_partitions: tuple[int, ...]
    partitions: tuple[int, ...]


@dataclass(frozen=True)
class ConsumedMessage:
    event_type: ClassVar[str] = "consumer.message"

    consumer_id: str
    partition: int
    offset: int
    key: str | None
    value: str
    timestamp_ms: int
    replayed: bool


@dataclass(frozen=True)
class OffsetCommitted:
    event_type: ClassVar[str] = "consumer.offset"

    consumer_id: str
    progress: PartitionProgress
