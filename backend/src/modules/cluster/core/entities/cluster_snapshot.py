from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar

from modules.cluster.core.entities.broker import BrokerState
from modules.cluster.core.entities.partition import PartitionState


@dataclass(frozen=True)
class ClusterSnapshot:
    event_type: ClassVar[str] = "cluster.snapshot"

    topic: str
    brokers: tuple[BrokerState, ...]
    partitions: tuple[PartitionState, ...]
    controller_id: int | None
    metadata_available: bool
    reachable_brokers: int
    quorum_voters: int
    quorum_ok: bool
    writes_ok: bool
    min_insync_replicas: int
    taken_at: datetime

    def reachable_broker_ids(self) -> frozenset[int]:
        return frozenset(broker.broker_id for broker in self.brokers if broker.reachable)

    def partition(self, partition_id: int) -> PartitionState | None:
        return next((partition for partition in self.partitions if partition.partition == partition_id), None)
