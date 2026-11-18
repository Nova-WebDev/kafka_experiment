import asyncio
from collections.abc import Iterator
from contextlib import contextmanager

from aiokafka import AIOKafkaConsumer, ConsumerRecord, TopicPartition
from aiokafka.abc import ConsumerRebalanceListener
from aiokafka.errors import KafkaError

from modules.consumer.core.entities.fetched_record import FetchedRecord
from modules.consumer.core.errors.consumer_errors import ConsumerConnectionError, OffsetCommitError
from modules.consumer.core.interfaces.consumer_client import ConsumerClient, ConsumerClientFactory, RebalanceHandler


class _RebalanceListener(ConsumerRebalanceListener):
    def __init__(self, handler: RebalanceHandler) -> None:
        self._handler = handler

    async def on_partitions_revoked(self, revoked: set[TopicPartition]) -> None:
        await self._handler.on_partitions_revoked({partition.partition for partition in revoked})

    async def on_partitions_assigned(self, assigned: set[TopicPartition]) -> None:
        await self._handler.on_partitions_assigned({partition.partition for partition in assigned})


class AiokafkaConsumerClient(ConsumerClient):
    def __init__(
        self,
        consumer: AIOKafkaConsumer,
        topic: str,
        rebalance_handler: RebalanceHandler,
        commit_timeout_seconds: float,
    ) -> None:
        self._consumer = consumer
        self._topic = topic
        self._rebalance_handler = rebalance_handler
        self._commit_timeout_seconds = commit_timeout_seconds
        self._rotation = 0
        self._commit_in_flight: asyncio.Task[None] | None = None

    async def start(self) -> None:
        self._consumer.subscribe([self._topic], listener=_RebalanceListener(self._rebalance_handler))
        with _as_connection_error():
            await self._consumer.start()

    async def close(self) -> None:
        await self._consumer.stop()

    async def fetch_one(self, timeout_ms: int) -> FetchedRecord | None:
        with _as_connection_error():
            for partition in self._partitions_in_turn():
                record = await self._take_one(timeout_ms=0, partitions=(partition,))
                if record is not None:
                    return record
            return await self._take_one(timeout_ms=timeout_ms, partitions=())

    def _partitions_in_turn(self) -> list[TopicPartition]:
        paused = self._consumer.paused()
        readable = sorted(
            (partition for partition in self._consumer.assignment() if partition not in paused),
            key=lambda partition: partition.partition,
        )
        if not readable:
            return []
        self._rotation = (self._rotation + 1) % len(readable)
        return readable[self._rotation :] + readable[: self._rotation]

    async def _take_one(self, timeout_ms: int, partitions: tuple[TopicPartition, ...]) -> FetchedRecord | None:
        batches = await self._consumer.getmany(*partitions, timeout_ms=timeout_ms, max_records=1)
        for records in batches.values():
            for record in records:
                return _to_fetched_record(record)
        return None

    async def commit(self, partition: int, offset: int) -> None:
        if self._commit_in_flight is not None and not self._commit_in_flight.done():
            raise OffsetCommitError("PreviousCommitStillPending")
        commit = asyncio.create_task(self._consumer.commit({self._partition(partition): offset}))
        commit.add_done_callback(_observe_outcome)
        self._commit_in_flight = commit
        done, _ = await asyncio.wait({commit}, timeout=self._commit_timeout_seconds)
        if not done:
            raise OffsetCommitError("CommitTimeout")
        error = commit.exception()
        if error is not None:
            raise OffsetCommitError(type(error).__name__) from error

    async def committed(self, partition: int) -> int | None:
        with _as_connection_error():
            return await self._consumer.committed(self._partition(partition))

    async def beginning_offsets(self, partitions: set[int]) -> dict[int, int]:
        with _as_connection_error():
            offsets = await self._consumer.beginning_offsets(self._partitions(partitions))
        return _by_partition_number(offsets)

    async def end_offsets(self, partitions: set[int]) -> dict[int, int]:
        with _as_connection_error():
            offsets = await self._consumer.end_offsets(self._partitions(partitions))
        return _by_partition_number(offsets)

    def pause_all(self) -> None:
        self._consumer.pause(*self._consumer.assignment())

    def resume_all(self) -> None:
        self._consumer.resume(*self._consumer.assignment())

    def seek(self, partition: int, offset: int) -> None:
        topic_partition = self._partition(partition)
        if topic_partition in self._consumer.assignment():
            self._consumer.seek(topic_partition, offset)

    def _partition(self, partition: int) -> TopicPartition:
        return TopicPartition(self._topic, partition)

    def _partitions(self, partitions: set[int]) -> list[TopicPartition]:
        return [self._partition(partition) for partition in partitions]


class AiokafkaConsumerClientFactory(ConsumerClientFactory):
    def __init__(
        self,
        bootstrap_servers: list[str],
        topic: str,
        session_timeout_ms: int,
        heartbeat_interval_ms: int,
        commit_timeout_seconds: float,
    ) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._topic = topic
        self._session_timeout_ms = session_timeout_ms
        self._heartbeat_interval_ms = heartbeat_interval_ms
        self._commit_timeout_seconds = commit_timeout_seconds

    def create(self, group_id: str, rebalance_handler: RebalanceHandler) -> ConsumerClient:
        consumer = AIOKafkaConsumer(
            bootstrap_servers=self._bootstrap_servers,
            group_id=group_id,
            client_id=f"kafka-lab-{group_id}",
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            session_timeout_ms=self._session_timeout_ms,
            heartbeat_interval_ms=self._heartbeat_interval_ms,
        )
        return AiokafkaConsumerClient(consumer, self._topic, rebalance_handler, self._commit_timeout_seconds)


@contextmanager
def _as_connection_error() -> Iterator[None]:
    try:
        yield
    except KafkaError as error:
        raise ConsumerConnectionError(type(error).__name__) from error


def _by_partition_number(offsets: dict[TopicPartition, int]) -> dict[int, int]:
    return {topic_partition.partition: offset for topic_partition, offset in offsets.items()}


def _observe_outcome(task: asyncio.Task[None]) -> None:
    if not task.cancelled():
        task.exception()


def _to_fetched_record(record: ConsumerRecord) -> FetchedRecord:
    return FetchedRecord(
        partition=record.partition,
        offset=record.offset,
        key=_decode(record.key),
        value=_decode(record.value) or "",
        timestamp_ms=record.timestamp,
    )


def _decode(raw: bytes | None) -> str | None:
    return raw.decode("utf-8", errors="replace") if raw is not None else None
