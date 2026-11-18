from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from di.kernel_providers import get_event_bus, get_retry_policy, get_settings
from modules.producer.core.interfaces.message_publisher import MessagePublisher
from modules.producer.core.use_cases.connect_producer import ConnectProducer
from modules.producer.core.use_cases.generate_order import OrderGenerator
from modules.producer.core.use_cases.run_auto_producer import RunAutoProducer
from modules.producer.core.use_cases.send_message import SendMessage
from modules.producer.core.use_cases.send_order import SendOrder
from modules.producer.infrastructure.aiokafka_message_publisher import AiokafkaMessagePublisher


@lru_cache
def get_message_publisher() -> MessagePublisher:
    settings = get_settings()
    return AiokafkaMessagePublisher(
        bootstrap_servers=settings.bootstrap_servers,
        topic=settings.topic_name,
        request_timeout_ms=settings.producer_request_timeout_ms,
    )


@lru_cache
def get_connect_producer() -> ConnectProducer:
    return ConnectProducer(get_message_publisher(), get_retry_policy())


@lru_cache
def get_send_message() -> SendMessage:
    return SendMessage(get_message_publisher(), get_event_bus())


@lru_cache
def get_send_order() -> SendOrder:
    return SendOrder(get_send_message(), OrderGenerator())


@lru_cache
def get_auto_producer() -> RunAutoProducer:
    return RunAutoProducer(get_send_order(), get_event_bus())


SendMessageDependency = Annotated[SendMessage, Depends(get_send_message)]
SendOrderDependency = Annotated[SendOrder, Depends(get_send_order)]
AutoProducerDependency = Annotated[RunAutoProducer, Depends(get_auto_producer)]
