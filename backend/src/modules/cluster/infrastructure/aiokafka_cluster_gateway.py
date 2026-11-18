import asyncio
import random
from typing import Any

from aiokafka.client import AIOKafkaClient
from aiokafka.errors import KafkaError, UnknownTopicOrPartitionError, for_code
from aiokafka.errors import TopicAlreadyExistsError as KafkaTopicAlreadyExistsError
from aiokafka.protocol.admin import CreateTopicsRequest, DeleteTopicsRequest
from aiokafka.protocol.api import Request, Response
from aiokafka.protocol.metadata import MetadataRequest

from modules.cluster.core.entities.cluster_metadata import ClusterMetadata
from modules.cluster.core.entities.partition import PartitionState
from modules.cluster.core.entities.topic import TopicSpec
from modules.cluster.core.errors.cluster_errors import (
    ClusterUnavailableError,
    TopicAlreadyExistsError,
    TopicOperationError,
)
from modules.cluster.core.interfaces.cluster_gateway import ClusterGateway
from modules.cluster.infrastructure.describe_quorum_protocol import NO_LEADER, DescribeQuorumRequest, quorum_leader_id

KAFKA_FAILURES = (KafkaError, OSError, TimeoutError)
NO_ERROR = 0


class AiokafkaClusterGateway(ClusterGateway):
    def __init__(
        self,
        bootstrap_servers: list[str],
        request_timeout_seconds: float,
        admin_timeout_seconds: float = 10.0,
        client_metadata_max_age_ms: int = 5000,
    ) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._request_timeout_seconds = request_timeout_seconds
        self._admin_timeout_seconds = admin_timeout_seconds
        self._client_metadata_max_age_ms = client_metadata_max_age_ms
        self._client: AIOKafkaClient | None = None
        self._preferred_node_id: int | None = None

    async def connect(self) -> None:
        await self.close()
        client = AIOKafkaClient(
            bootstrap_servers=self._bootstrap_servers,
            client_id="kafka-lab-cluster",
            request_timeout_ms=int(self._admin_timeout_seconds * 1000),
            metadata_max_age_ms=self._client_metadata_max_age_ms,
        )
        try:
            await client.bootstrap()
        except KAFKA_FAILURES as error:
            await client.close()
            raise ClusterUnavailableError(f"Bootstrap failed: {type(error).__name__}") from error
        self._client = client

    async def close(self) -> None:
        client, self._client = self._client, None
        if client is not None:
            await client.close()

    async def fetch_metadata(self, topic: str) -> ClusterMetadata:
        response = (await self._send_to_any_broker(MetadataRequest([topic], False))).to_object()
        return ClusterMetadata(
            broker_ids=frozenset(broker["node_id"] for broker in response["brokers"]),
            controller_id=await self._fetch_active_controller(),
            partitions=_partitions_of(response, topic),
        )

    async def topic_exists(self, topic: str) -> bool:
        response = (await self._send_to_any_broker(MetadataRequest([topic], False))).to_object()
        return any(entry["topic"] == topic and entry["error_code"] == NO_ERROR for entry in response["topics"])

    async def create_topic(self, spec: TopicSpec) -> None:
        request = CreateTopicsRequest(
            create_topic_requests=[
                (
                    spec.name,
                    spec.partitions,
                    spec.replication_factor,
                    [],
                    [("min.insync.replicas", str(spec.min_insync_replicas))],
                )
            ],
            timeout=self._admin_timeout_ms,
            validate_only=False,
        )
        response = await self._send_to_any_broker(request, self._admin_timeout_seconds)
        for result in response.to_object()["topic_errors"]:
            error_type = for_code(result["error_code"])
            if result["error_code"] == NO_ERROR:
                continue
            if error_type is KafkaTopicAlreadyExistsError:
                raise TopicAlreadyExistsError(spec.name)
            raise TopicOperationError(f"Creating {spec.name} failed: {error_type.__name__}")

    async def delete_topic(self, topic: str) -> None:
        request = DeleteTopicsRequest([topic], self._admin_timeout_ms)
        response = await self._send_to_any_broker(request, self._admin_timeout_seconds)
        for result in response.to_object()["topic_error_codes"]:
            error_type = for_code(result["error_code"])
            if result["error_code"] == NO_ERROR or error_type is UnknownTopicOrPartitionError:
                continue
            raise TopicOperationError(f"Deleting {topic} failed: {error_type.__name__}")

    @property
    def _admin_timeout_ms(self) -> int:
        return int(self._admin_timeout_seconds * 1000)

    async def _fetch_active_controller(self) -> int | None:
        client = self._connected_client()
        node_id = self._preferred_node_id
        if node_id is None:
            return None
        try:
            response = await self._send(client, node_id, DescribeQuorumRequest(), self._request_timeout_seconds)
        except KAFKA_FAILURES:
            return None
        return quorum_leader_id(response)

    async def _send_to_any_broker(self, request: Request, timeout_seconds: float | None = None) -> Response:
        client = self._connected_client()
        for node_id in self._candidate_nodes(client):
            try:
                response = await self._send(client, node_id, request, timeout_seconds or self._request_timeout_seconds)
            except KAFKA_FAILURES:
                continue
            self._preferred_node_id = node_id
            return response
        raise ClusterUnavailableError("No broker answered")

    @staticmethod
    async def _send(client: AIOKafkaClient, node_id: int, request: Request, timeout_seconds: float) -> Response:
        async with asyncio.timeout(timeout_seconds):
            return await client.send(node_id, request)

    def _candidate_nodes(self, client: AIOKafkaClient) -> list[int]:
        node_ids = [broker.nodeId for broker in client.cluster.brokers()]
        random.shuffle(node_ids)
        if self._preferred_node_id in node_ids:
            node_ids.remove(self._preferred_node_id)
            node_ids.insert(0, self._preferred_node_id)
        return node_ids

    def _connected_client(self) -> AIOKafkaClient:
        if self._client is None:
            raise ClusterUnavailableError("Not connected")
        return self._client


def _partitions_of(response: dict[str, Any], topic: str) -> tuple[PartitionState, ...]:
    for entry in response["topics"]:
        if entry["topic"] != topic or entry["error_code"] != NO_ERROR:
            continue
        partitions = (
            PartitionState(
                partition=partition["partition"],
                leader=None if partition["leader"] == NO_LEADER else partition["leader"],
                replicas=tuple(partition["replicas"]),
                isr=tuple(sorted(partition["isr"])),
            )
            for partition in entry["partitions"]
        )
        return tuple(sorted(partitions, key=lambda partition: partition.partition))
    return ()
