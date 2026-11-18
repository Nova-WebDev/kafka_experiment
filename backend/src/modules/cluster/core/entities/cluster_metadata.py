from dataclasses import dataclass

from modules.cluster.core.entities.partition import PartitionState


@dataclass(frozen=True)
class ClusterMetadata:
    broker_ids: frozenset[int]
    controller_id: int | None
    partitions: tuple[PartitionState, ...]
