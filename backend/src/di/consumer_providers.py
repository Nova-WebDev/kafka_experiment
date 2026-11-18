from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from di.kernel_providers import get_event_bus, get_retry_policy, get_settings
from modules.consumer.core.entities.consumer_tuning import ConsumerTuning
from modules.consumer.core.interfaces.consumer_registry import ConsumerRegistry
from modules.consumer.core.use_cases.command_consumer import CommandConsumer
from modules.consumer.core.use_cases.create_consumer import CreateConsumer
from modules.consumer.core.use_cases.list_consumers import ListConsumers
from modules.consumer.core.use_cases.remove_consumer import RemoveConsumer
from modules.consumer.infrastructure.aiokafka_consumer_client import AiokafkaConsumerClientFactory
from modules.consumer.infrastructure.in_memory_consumer_registry import InMemoryConsumerRegistry


@lru_cache
def get_consumer_registry() -> ConsumerRegistry:
    return InMemoryConsumerRegistry()


@lru_cache
def get_create_consumer() -> CreateConsumer:
    settings = get_settings()
    return CreateConsumer(
        registry=get_consumer_registry(),
        client_factory=AiokafkaConsumerClientFactory(
            bootstrap_servers=settings.bootstrap_servers,
            topic=settings.topic_name,
            session_timeout_ms=settings.consumer_session_timeout_ms,
            heartbeat_interval_ms=settings.consumer_heartbeat_interval_ms,
            commit_timeout_seconds=settings.consumer_commit_timeout_seconds,
        ),
        event_bus=get_event_bus(),
        retry_policy=get_retry_policy(),
        tuning=ConsumerTuning(
            fetch_timeout_ms=settings.consumer_fetch_timeout_ms,
            watermark_refresh_seconds=settings.consumer_watermark_refresh_seconds,
            broker_call_timeout_seconds=settings.consumer_broker_call_timeout_seconds,
            recent_messages_limit=settings.consumer_recent_messages,
        ),
    )


@lru_cache
def get_remove_consumer() -> RemoveConsumer:
    return RemoveConsumer(get_consumer_registry(), get_event_bus())


@lru_cache
def get_command_consumer() -> CommandConsumer:
    return CommandConsumer(get_consumer_registry())


@lru_cache
def get_list_consumers() -> ListConsumers:
    return ListConsumers(get_consumer_registry())


CreateConsumerDependency = Annotated[CreateConsumer, Depends(get_create_consumer)]
RemoveConsumerDependency = Annotated[RemoveConsumer, Depends(get_remove_consumer)]
CommandConsumerDependency = Annotated[CommandConsumer, Depends(get_command_consumer)]
ListConsumersDependency = Annotated[ListConsumers, Depends(get_list_consumers)]
