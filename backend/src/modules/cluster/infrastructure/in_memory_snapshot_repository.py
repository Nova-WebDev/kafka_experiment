from modules.cluster.core.entities.cluster_snapshot import ClusterSnapshot
from modules.cluster.core.interfaces.snapshot_repository import SnapshotRepository


class InMemorySnapshotRepository(SnapshotRepository):
    def __init__(self) -> None:
        self._latest: ClusterSnapshot | None = None

    def latest(self) -> ClusterSnapshot | None:
        return self._latest

    def save(self, snapshot: ClusterSnapshot) -> None:
        self._latest = snapshot
