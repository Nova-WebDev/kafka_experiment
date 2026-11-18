from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from di.kernel_providers import get_event_bus, get_retry_policy, get_settings
from modules.cluster.core.entities.broker import BrokerAddress
from modules.cluster.core.entities.topic import TopicSpec
from modules.cluster.core.interfaces.cluster_gateway import ClusterGateway
from modules.cluster.core.interfaces.snapshot_repository import SnapshotRepository
from modules.cluster.core.use_cases.ensure_topic import EnsureTopic
from modules.cluster.core.use_cases.monitor_cluster import MonitorCluster
from modules.cluster.core.use_cases.reset_topic import ResetTopic
from modules.cluster.infrastructure.aiokafka_cluster_gateway import AiokafkaClusterGateway
from modules.cluster.infrastructure.in_memory_snapshot_repository import InMemorySnapshotRepository
from modules.cluster.infrastructure.tcp_broker_probe import TcpBrokerProbe


@lru_cache
def get_topic_spec() -> TopicSpec:
    settings = get_settings()
    return TopicSpec(
        name=settings.topic_name,
        partitions=settings.topic_partitions,
        replication_factor=settings.topic_replication_factor,
        min_insync_replicas=settings.min_insync_replicas,
    )


@lru_cache
def get_broker_addresses() -> tuple[BrokerAddress, ...]:
    settings = get_settings()
    return tuple(
        BrokerAddress(broker_id=broker_id, host=settings.broker_host(broker_id), port=settings.broker_port)
        for broker_id in settings.broker_ids
    )


@lru_cache
def get_cluster_gateway() -> ClusterGateway:
    settings = get_settings()
    return AiokafkaClusterGateway(
        bootstrap_servers=settings.bootstrap_servers,
        request_timeout_seconds=settings.kafka_request_timeout_seconds,
    )


@lru_cache
def get_snapshot_repository() -> SnapshotRepository:
    return InMemorySnapshotRepository()


@lru_cache
def get_ensure_topic() -> EnsureTopic:
    return EnsureTopic(get_cluster_gateway(), get_topic_spec())


@lru_cache
def get_reset_topic() -> ResetTopic:
    return ResetTopic(get_cluster_gateway(), get_topic_spec(), get_event_bus())


@lru_cache
def get_cluster_monitor() -> MonitorCluster:
    settings = get_settings()
    return MonitorCluster(
        gateway=get_cluster_gateway(),
        probe=TcpBrokerProbe(settings.broker_probe_timeout_seconds),
        snapshots=get_snapshot_repository(),
        ensure_topic=get_ensure_topic(),
        event_bus=get_event_bus(),
        retry_policy=get_retry_policy(),
        brokers=get_broker_addresses(),
        topic=get_topic_spec(),
        poll_interval_seconds=settings.cluster_poll_interval_seconds,
    )


ClusterMonitorDependency = Annotated[MonitorCluster, Depends(get_cluster_monitor)]
ResetTopicDependency = Annotated[ResetTopic, Depends(get_reset_topic)]
