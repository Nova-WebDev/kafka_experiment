import asyncio
import logging
from collections import deque
from contextlib import suppress

from app.event_bus import EventBus, History, PublishedEvent
from app.retry_policy import ConnectionRetryPolicy
from modules.consumer.core.entities.commands import (
    ChangeDelay,
    ConsumerCommand,
    PauseConsumption,
    ResumeConsumption,
    SeekPartition,
)
from modules.consumer.core.entities.consumer_events import ConsumedMessage, ConsumerRebalanced, OffsetCommitted
from modules.consumer.core.entities.consumer_state import ConsumerState, ConsumerStatus
from modules.consumer.core.entities.consumer_tuning import ConsumerTuning
from modules.consumer.core.entities.fetched_record import FetchedRecord
from modules.consumer.core.entities.partition_cursor import PartitionCursor
from modules.consumer.core.errors.consumer_errors import ConsumerConnectionError, OffsetCommitError
from modules.consumer.core.interfaces.consumer_client import ConsumerClient, ConsumerClientFactory, RebalanceHandler

logger = logging.getLogger(__name__)


class DemoConsumer(RebalanceHandler):
    def __init__(
        self,
        *,
        consumer_id: str,
        group_id: str,
        delay_ms: int,
        client_factory: ConsumerClientFactory,
        event_bus: EventBus,
        retry_policy: ConnectionRetryPolicy,
        tuning: ConsumerTuning,
    ) -> None:
        self.consumer_id = consumer_id
        self.group_id = group_id
        self._delay_ms = delay_ms
        self._client_factory = client_factory
        self._event_bus = event_bus
        self._retry_policy = retry_policy
        self._tuning = tuning
        self._commands: asyncio.Queue[ConsumerCommand] = asyncio.Queue()
        self._status = ConsumerStatus.RUNNING
        self._paused = False
        self._cursors: dict[int, PartitionCursor] = {}
        self._uninitialized_partitions: set[int] = set()
        self._highest_processed: dict[int, int] = {}
        self._previous_assignment: tuple[int, ...] = ()
        self._recent_messages: deque[PublishedEvent] = deque(maxlen=tuning.recent_messages_limit)
        self._task: asyncio.Task[None] | None = None

    @property
    def connection_source(self) -> str:
        return f"consumer {self.consumer_id}"

    def state(self) -> ConsumerState:
        return ConsumerState(
            consumer_id=self.consumer_id,
            group_id=self.group_id,
            status=self._status,
            delay_ms=self._delay_ms,
            partitions=tuple(self._cursors[partition].to_progress() for partition in sorted(self._cursors)),
        )

    def recent_messages(self) -> list[PublishedEvent]:
        return list(self._recent_messages)

    def submit(self, command: ConsumerCommand) -> None:
        self._commands.put_nowait(command)

    def start(self) -> None:
        self._task = asyncio.create_task(self._run(), name=f"consumer-{self.consumer_id}")

    async def stop(self) -> None:
        task, self._task = self._task, None
        if task is not None:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
        self._status = ConsumerStatus.STOPPED

    async def on_partitions_revoked(self, partitions: set[int]) -> None:
        self._previous_assignment = tuple(sorted(self._cursors))
        for partition in partitions:
            self._cursors.pop(partition, None)
            self._uninitialized_partitions.discard(partition)

    async def on_partitions_assigned(self, partitions: set[int]) -> None:
        for partition in partitions:
            self._cursors.setdefault(partition, PartitionCursor(partition))
            self._uninitialized_partitions.add(partition)
        rebalanced = ConsumerRebalanced(
            consumer_id=self.consumer_id,
            group_id=self.group_id,
            previous_partitions=self._previous_assignment,
            partitions=tuple(sorted(self._cursors)),
        )
        self._event_bus.publish(rebalanced.event_type, rebalanced, history=History.TIMELINE)
        self._publish_state()

    async def _run(self) -> None:
        while True:
            client = await self._retry_policy.connect(self.connection_source, self._open_client)
            try:
                self._set_status(ConsumerStatus.PAUSED if self._paused else ConsumerStatus.RUNNING)
                await self._consume(client)
            except ConsumerConnectionError as error:
                logger.warning("consumer %s lost its connection: %s", self.consumer_id, error)
                self._set_status(ConsumerStatus.RECONNECTING)
            finally:
                await client.close()

    async def _open_client(self) -> ConsumerClient:
        client = self._client_factory.create(self.group_id, self)
        try:
            await client.start()
        except BaseException:
            self._set_status(ConsumerStatus.RECONNECTING)
            await client.close()
            raise
        return client

    async def _consume(self, client: ConsumerClient) -> None:
        loop = asyncio.get_running_loop()
        next_watermark_refresh = loop.time()
        while True:
            await self._apply_commands(client)
            await self._initialize_partitions(client)
            if loop.time() >= next_watermark_refresh:
                await self._refresh_watermarks(client)
                next_watermark_refresh = loop.time() + self._tuning.watermark_refresh_seconds
            if self._paused:
                client.pause_all()
            record = await client.fetch_one(self._tuning.fetch_timeout_ms)
            if record is not None:
                await self._process(client, record)

    async def _process(self, client: ConsumerClient, record: FetchedRecord) -> None:
        cursor = self._cursors.get(record.partition)
        if cursor is None:
            return
        message = ConsumedMessage(
            consumer_id=self.consumer_id,
            partition=record.partition,
            offset=record.offset,
            key=record.key,
            value=record.value,
            timestamp_ms=record.timestamp_ms,
            replayed=record.offset <= self._highest_processed.get(record.partition, -1),
        )
        self._recent_messages.append(self._event_bus.publish(message.event_type, message))
        cursor.position = record.offset + 1
        cursor.high_watermark = max(cursor.high_watermark or 0, record.offset + 1)
        if self._delay_ms > 0:
            await asyncio.sleep(self._delay_ms / 1000)
        self._highest_processed[record.partition] = max(
            record.offset, self._highest_processed.get(record.partition, -1)
        )
        await self._commit(client, cursor, record.offset + 1)

    async def _commit(self, client: ConsumerClient, cursor: PartitionCursor, offset: int) -> None:
        try:
            await client.commit(cursor.partition, offset)
        except OffsetCommitError as error:
            logger.warning("consumer %s could not commit P%d@%d: %s", self.consumer_id, cursor.partition, offset, error)
            return
        cursor.committed = offset
        committed = OffsetCommitted(consumer_id=self.consumer_id, progress=cursor.to_progress())
        self._event_bus.publish(committed.event_type, committed)

    async def _apply_commands(self, client: ConsumerClient) -> None:
        while not self._commands.empty():
            command = self._commands.get_nowait()
            match command:
                case PauseConsumption():
                    self._paused = True
                    client.pause_all()
                    self._set_status(ConsumerStatus.PAUSED)
                case ResumeConsumption():
                    self._paused = False
                    client.resume_all()
                    self._set_status(ConsumerStatus.RUNNING)
                case ChangeDelay(delay_ms=delay_ms):
                    self._delay_ms = delay_ms
                    self._publish_state()
                case SeekPartition(partition=partition, offset=offset):
                    self._seek(client, partition, offset)

    def _seek(self, client: ConsumerClient, partition: int, offset: int) -> None:
        cursor = self._cursors.get(partition)
        if cursor is None:
            return
        target = cursor.clamp(offset)
        client.seek(partition, target)
        cursor.position = target
        self._publish_state()

    async def _initialize_partitions(self, client: ConsumerClient) -> None:
        if not self._uninitialized_partitions:
            return
        partitions = set(self._uninitialized_partitions)
        try:
            async with asyncio.timeout(self._tuning.broker_call_timeout_seconds):
                beginnings = await client.beginning_offsets(partitions)
                committed = {partition: await client.committed(partition) for partition in partitions}
        except (TimeoutError, ConsumerConnectionError):
            return
        for partition in partitions:
            cursor = self._cursors.get(partition)
            if cursor is None:
                continue
            cursor.log_start = beginnings.get(partition, 0)
            cursor.committed = committed[partition]
            cursor.position = committed[partition] if committed[partition] is not None else cursor.log_start
        self._uninitialized_partitions -= partitions
        self._publish_state()

    async def _refresh_watermarks(self, client: ConsumerClient) -> None:
        partitions = set(self._cursors)
        if not partitions:
            return
        try:
            async with asyncio.timeout(self._tuning.broker_call_timeout_seconds):
                ends = await client.end_offsets(partitions)
        except (TimeoutError, ConsumerConnectionError):
            return
        for partition, end_offset in ends.items():
            cursor = self._cursors.get(partition)
            if cursor is not None:
                cursor.high_watermark = end_offset
        self._publish_state()

    def _set_status(self, status: ConsumerStatus) -> None:
        self._status = status
        self._publish_state()

    def _publish_state(self) -> None:
        state = self.state()
        self._event_bus.publish(state.event_type, state)
