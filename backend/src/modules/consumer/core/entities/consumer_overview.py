from dataclasses import dataclass

from app.event_bus import PublishedEvent
from modules.consumer.core.entities.consumer_state import ConsumerState


@dataclass(frozen=True)
class ConsumerOverview:
    state: ConsumerState
    recent_messages: tuple[PublishedEvent, ...]
