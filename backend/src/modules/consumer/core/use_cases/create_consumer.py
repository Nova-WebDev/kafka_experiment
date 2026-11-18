import secrets

from app.event_bus import EventBus, History
from app.retry_policy import ConnectionRetryPolicy
from modules.consumer.core.entities.consumer_events import ConsumerCreated
from modules.consumer.core.entities.consumer_state import ConsumerState
from modules.consumer.core.entities.consumer_tuning import ConsumerTuning
from modules.consumer.core.interfaces.consumer_client import ConsumerClientFactory
from modules.consumer.core.interfaces.consumer_registry import ConsumerRegistry
from modules.consumer.core.use_cases.demo_consumer import DemoConsumer


class CreateConsumer:
    def __init__(
        self,
        registry: ConsumerRegistry,
        client_factory: ConsumerClientFactory,
        event_bus: EventBus,
        retry_policy: ConnectionRetryPolicy,
        tuning: ConsumerTuning,
    ) -> None:
        self._registry = registry
        self._client_factory = client_factory
        self._event_bus = event_bus
        self._retry_policy = retry_policy
        self._tuning = tuning

    def execute(self, group_id: str | None, delay_ms: int) -> ConsumerState:
        consumer_id = self._registry.next_id()
        consumer = DemoConsumer(
            consumer_id=consumer_id,
            group_id=group_id or _new_group_id(consumer_id),
            delay_ms=delay_ms,
            client_factory=self._client_factory,
            event_bus=self._event_bus,
            retry_policy=self._retry_policy,
            tuning=self._tuning,
        )
        self._registry.add(consumer)
        consumer.start()
        state = consumer.state()
        created = ConsumerCreated(
            consumer_id=consumer_id,
            group_id=consumer.group_id,
            joined_existing_group=group_id is not None,
            state=state,
        )
        self._event_bus.publish(created.event_type, created, history=History.TIMELINE)
        return state


def _new_group_id(consumer_id: str) -> str:
    return f"group-{consumer_id.lower()}-{secrets.token_hex(2)}"
