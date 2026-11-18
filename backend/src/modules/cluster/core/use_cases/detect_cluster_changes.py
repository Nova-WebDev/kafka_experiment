from modules.cluster.core.entities.cluster_changes import (
    BrokerDown,
    BrokerUp,
    ClusterChange,
    ControllerChanged,
    IsrExpanded,
    IsrShrunk,
    LeaderChanged,
    QuorumLost,
    QuorumRestored,
    WritesBlocked,
    WritesRestored,
)
from modules.cluster.core.entities.cluster_snapshot import ClusterSnapshot


def detect_cluster_changes(previous: ClusterSnapshot | None, current: ClusterSnapshot) -> list[ClusterChange]:
    if previous is None:
        return []
    changes: list[ClusterChange] = []
    changes.extend(_broker_changes(previous, current))
    changes.extend(_quorum_changes(previous, current))
    if previous.metadata_available and current.metadata_available:
        changes.extend(_controller_changes(previous, current))
        changes.extend(_partition_changes(previous, current))
    if previous.partitions:
        changes.extend(_write_availability_changes(previous, current))
    return changes


def _broker_changes(previous: ClusterSnapshot, current: ClusterSnapshot) -> list[ClusterChange]:
    was_reachable = previous.reachable_broker_ids()
    is_reachable = current.reachable_broker_ids()
    went_down = [BrokerDown(broker_id) for broker_id in sorted(was_reachable - is_reachable)]
    came_up = [BrokerUp(broker_id) for broker_id in sorted(is_reachable - was_reachable)]
    return [*went_down, *came_up]


def _quorum_changes(previous: ClusterSnapshot, current: ClusterSnapshot) -> list[ClusterChange]:
    if previous.quorum_ok and not current.quorum_ok:
        return [QuorumLost(current.reachable_brokers, current.quorum_voters)]
    if not previous.quorum_ok and current.quorum_ok:
        return [QuorumRestored(current.reachable_brokers, current.quorum_voters)]
    return []


def _controller_changes(previous: ClusterSnapshot, current: ClusterSnapshot) -> list[ClusterChange]:
    if previous.controller_id == current.controller_id:
        return []
    return [ControllerChanged(previous.controller_id, current.controller_id)]


def _partition_changes(previous: ClusterSnapshot, current: ClusterSnapshot) -> list[ClusterChange]:
    changes: list[ClusterChange] = []
    for partition in current.partitions:
        before = previous.partition(partition.partition)
        if before is None:
            continue
        if before.leader != partition.leader:
            changes.append(LeaderChanged(partition.partition, before.leader, partition.leader))
        removed = tuple(sorted(set(before.isr) - set(partition.isr)))
        added = tuple(sorted(set(partition.isr) - set(before.isr)))
        if removed:
            changes.append(IsrShrunk(partition.partition, removed, partition.isr))
        if added:
            changes.append(IsrExpanded(partition.partition, added, partition.isr))
    return changes


def _write_availability_changes(previous: ClusterSnapshot, current: ClusterSnapshot) -> list[ClusterChange]:
    if previous.writes_ok and not current.writes_ok:
        reachable = current.reachable_broker_ids()
        blocked = tuple(
            partition.partition
            for partition in current.partitions
            if not partition.accepts_writes(reachable, current.min_insync_replicas)
        )
        return [WritesBlocked(blocked)]
    if not previous.writes_ok and current.writes_ok:
        return [WritesRestored()]
    return []
