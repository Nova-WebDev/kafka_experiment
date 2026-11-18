from abc import ABC, abstractmethod

from modules.cluster.core.entities.cluster_snapshot import ClusterSnapshot


class SnapshotRepository(ABC):
    @abstractmethod
    def latest(self) -> ClusterSnapshot | None: ...

    @abstractmethod
    def save(self, snapshot: ClusterSnapshot) -> None: ...
