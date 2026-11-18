from abc import ABC, abstractmethod

from modules.consumer.core.entities.fetched_record import FetchedRecord


class RebalanceHandler(ABC):
    @abstractmethod
    async def on_partitions_revoked(self, partitions: set[int]) -> None: ...

    @abstractmethod
    async def on_partitions_assigned(self, partitions: set[int]) -> None: ...


class ConsumerClient(ABC):
    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    async def fetch_one(self, timeout_ms: int) -> FetchedRecord | None: ...

    @abstractmethod
    async def commit(self, partition: int, offset: int) -> None: ...

    @abstractmethod
    async def committed(self, partition: int) -> int | None: ...

    @abstractmethod
    async def beginning_offsets(self, partitions: set[int]) -> dict[int, int]: ...

    @abstractmethod
    async def end_offsets(self, partitions: set[int]) -> dict[int, int]: ...

    @abstractmethod
    def pause_all(self) -> None: ...

    @abstractmethod
    def resume_all(self) -> None: ...

    @abstractmethod
    def seek(self, partition: int, offset: int) -> None: ...


class ConsumerClientFactory(ABC):
    @abstractmethod
    def create(self, group_id: str, rebalance_handler: RebalanceHandler) -> ConsumerClient: ...
