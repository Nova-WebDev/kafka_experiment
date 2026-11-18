import asyncio
from datetime import UTC, datetime

from app.event_bus import EventBus, History
from app.retry_policy import ConnectionRetryPolicy
from modules.cluster.core.entities.broker import BrokerAddress
from modules.cluster.core.entities.cluster_metadata import ClusterMetadata
from modules.cluster.core.entities.cluster_snapshot import ClusterSnapshot
from modules.cluster.core.entities.topic import TopicSpec
from modules.cluster.core.errors.cluster_errors import ClusterUnavailableError
from modules.cluster.core.interfaces.broker_probe import BrokerProbe
from modules.cluster.core.interfaces.cluster_gateway import ClusterGateway
from modules.cluster.core.interfaces.snapshot_repository import SnapshotRepository
from modules.cluster.core.use_cases.build_cluster_snapshot import build_cluster_snapshot
from modules.cluster.core.use_cases.detect_cluster_changes import detect_cluster_changes
from modules.cluster.core.use_cases.ensure_topic import EnsureTopic

CONNECTION_SOURCE = "cluster"


class MonitorCluster:
    def __init__(
        self,
        *,
        gateway: ClusterGateway,
        probe: BrokerProbe,
        snapshots: SnapshotRepository,
        ensure_topic: EnsureTopic,
        event_bus: EventBus,
        retry_policy: ConnectionRetryPolicy,
        brokers: tuple[BrokerAddress, ...],
        topic: TopicSpec,
        poll_interval_seconds: float,
    ) -> None:
        self._gateway = gateway
        self._probe = probe
        self._snapshots = snapshots
        self._ensure_topic = ensure_topic
        self._event_bus = event_bus
        self._retry_policy = retry_policy
        self._brokers = brokers
        self._topic = topic
        self._poll_interval_seconds = poll_interval_seconds
        self._metadata: ClusterMetadata | None = None
        self._reachable_broker_ids: frozenset[int] | None = None

    def current_snapshot(self) -> ClusterSnapshot | None:
        return self._snapshots.latest()

    async def run(self) -> None:
        async with asyncio.TaskGroup() as tasks:
            tasks.create_task(self._follow_metadata())
            tasks.create_task(self._publish_snapshots())

    async def _follow_metadata(self) -> None:
        while True:
            await self._retry_policy.connect(CONNECTION_SOURCE, self._connect)
            await self._refresh_metadata_until_lost()

    async def _connect(self) -> None:
        await self._gateway.connect()
        await self._ensure_topic.execute()
        self._metadata = await self._gateway.fetch_metadata(self._topic.name)

    async def _refresh_metadata_until_lost(self) -> None:
        while True:
            await asyncio.sleep(self._poll_interval_seconds)
            if self._reachable_broker_ids == frozenset():
                self._metadata = None
                return
            try:
                self._metadata = await self._gateway.fetch_metadata(self._topic.name)
            except ClusterUnavailableError:
                self._metadata = None
                return

    async def _publish_snapshots(self) -> None:
        while True:
            reachable_broker_ids = await self._probe_brokers()
            self._reachable_broker_ids = reachable_broker_ids
            previous = self._snapshots.latest()
            snapshot = build_cluster_snapshot(
                brokers=self._brokers,
                reachable_broker_ids=reachable_broker_ids,
                metadata=self._metadata,
                previous=previous,
                topic=self._topic,
                taken_at=datetime.now(UTC),
            )
            for change in detect_cluster_changes(previous, snapshot):
                self._event_bus.publish(change.event_type, change, history=History.TIMELINE)
            self._snapshots.save(snapshot)
            self._event_bus.publish(snapshot.event_type, snapshot)
            await asyncio.sleep(self._poll_interval_seconds)

    async def _probe_brokers(self) -> frozenset[int]:
        results = await asyncio.gather(*(self._probe.is_reachable(address) for address in self._brokers))
        probed = zip(self._brokers, results, strict=True)
        return frozenset(address.broker_id for address, reachable in probed if reachable)
