from datetime import datetime

from modules.cluster.core.entities.broker import BrokerAddress, BrokerState
from modules.cluster.core.entities.cluster_metadata import ClusterMetadata
from modules.cluster.core.entities.cluster_snapshot import ClusterSnapshot
from modules.cluster.core.entities.partition import PartitionState
from modules.cluster.core.entities.topic import TopicSpec


def build_cluster_snapshot(
    *,
    brokers: tuple[BrokerAddress, ...],
    reachable_broker_ids: frozenset[int],
    metadata: ClusterMetadata | None,
    previous: ClusterSnapshot | None,
    topic: TopicSpec,
    taken_at: datetime,
) -> ClusterSnapshot:
    partitions = _partitions(metadata, previous)
    controller_id = metadata.controller_id if metadata else None
    metadata_broker_ids = metadata.broker_ids if metadata else frozenset()
    quorum_size = len(brokers) // 2 + 1
    return ClusterSnapshot(
        topic=topic.name,
        brokers=tuple(
            BrokerState(
                broker_id=address.broker_id,
                host=address.host,
                reachable=address.broker_id in reachable_broker_ids,
                in_metadata=address.broker_id in metadata_broker_ids,
                is_controller=address.broker_id == controller_id,
                leader_count=sum(1 for partition in partitions if partition.leader == address.broker_id),
            )
            for address in brokers
        ),
        partitions=partitions,
        controller_id=controller_id,
        metadata_available=metadata is not None,
        reachable_brokers=len(reachable_broker_ids),
        quorum_voters=len(brokers),
        quorum_ok=len(reachable_broker_ids) >= quorum_size,
        writes_ok=metadata is not None
        and len(partitions) > 0
        and all(partition.accepts_writes(reachable_broker_ids, topic.min_insync_replicas) for partition in partitions),
        min_insync_replicas=topic.min_insync_replicas,
        taken_at=taken_at,
    )


def _partitions(metadata: ClusterMetadata | None, previous: ClusterSnapshot | None) -> tuple[PartitionState, ...]:
    if metadata is not None:
        return metadata.partitions
    if previous is not None:
        return previous.partitions
    return ()
