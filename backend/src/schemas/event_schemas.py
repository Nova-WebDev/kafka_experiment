from datetime import datetime
from typing import Any

from pydantic import BaseModel
from sse_starlette import ServerSentEvent

from app.event_bus import History, PublishedEvent


class EventEnvelope(BaseModel):
    id: str
    type: str
    at: datetime
    payload: Any

    @classmethod
    def of(cls, event: PublishedEvent) -> "EventEnvelope":
        return cls(id=event.id, type=event.type, at=event.published_at, payload=event.payload)


class EventHistory(BaseModel):
    events: list[EventEnvelope]


def to_server_sent_event(event: PublishedEvent) -> ServerSentEvent:
    return ServerSentEvent(
        id=event.id,
        event=event.type,
        data=EventEnvelope.of(event).model_dump_json(),
    )


def history_event(history: History, events: list[PublishedEvent]) -> ServerSentEvent:
    payload = EventHistory(events=[EventEnvelope.of(event) for event in events])
    return ServerSentEvent(event=f"{history}.history", data=payload.model_dump_json())
