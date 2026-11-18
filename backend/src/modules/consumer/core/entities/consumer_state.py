from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar


class ConsumerStatus(StrEnum):
    RUNNING = "running"
    PAUSED = "paused"
    RECONNECTING = "reconnecting"
    STOPPED = "stopped"


@dataclass(frozen=True)
class PartitionProgress:
    partition: int
    position: int | None
    committed: int | None
    high_watermark: int | None
    lag: int | None


@dataclass(frozen=True)
class ConsumerState:
    event_type: ClassVar[str] = "consumer.state"

    consumer_id: str
    group_id: str
    status: ConsumerStatus
    delay_ms: int
    partitions: tuple[PartitionProgress, ...]
