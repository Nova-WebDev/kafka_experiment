from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class ClusterChange:
    event_type: ClassVar[str]


@dataclass(frozen=True)
class BrokerDown(ClusterChange):
    event_type: ClassVar[str] = "broker.down"

    broker_id: int


@dataclass(frozen=True)
class BrokerUp(ClusterChange):
    event_type: ClassVar[str] = "broker.up"

    broker_id: int


@dataclass(frozen=True)
class ControllerChanged(ClusterChange):
    event_type: ClassVar[str] = "controller.changed"

    previous_controller_id: int | None
    controller_id: int | None


@dataclass(frozen=True)
class LeaderChanged(ClusterChange):
    event_type: ClassVar[str] = "leader.changed"

    partition: int
    previous_leader: int | None
    leader: int | None


@dataclass(frozen=True)
class IsrShrunk(ClusterChange):
    event_type: ClassVar[str] = "isr.shrunk"

    partition: int
    removed: tuple[int, ...]
    isr: tuple[int, ...]


@dataclass(frozen=True)
class IsrExpanded(ClusterChange):
    event_type: ClassVar[str] = "isr.expanded"

    partition: int
    added: tuple[int, ...]
    isr: tuple[int, ...]


@dataclass(frozen=True)
class QuorumLost(ClusterChange):
    event_type: ClassVar[str] = "quorum.lost"

    reachable_voters: int
    quorum_voters: int


@dataclass(frozen=True)
class QuorumRestored(ClusterChange):
    event_type: ClassVar[str] = "quorum.restored"

    reachable_voters: int
    quorum_voters: int


@dataclass(frozen=True)
class WritesBlocked(ClusterChange):
    event_type: ClassVar[str] = "writes.blocked"

    blocked_partitions: tuple[int, ...]


@dataclass(frozen=True)
class WritesRestored(ClusterChange):
    event_type: ClassVar[str] = "writes.restored"
