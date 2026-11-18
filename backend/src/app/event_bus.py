import asyncio
from collections import defaultdict, deque
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4


class History(StrEnum):
    TIMELINE = "timeline"
    PRODUCER = "producer"


@dataclass(frozen=True)
class PublishedEvent:
    id: str
    type: str
    payload: object
    published_at: datetime

    @classmethod
    def create(cls, event_type: str, payload: object) -> "PublishedEvent":
        return cls(id=uuid4().hex, type=event_type, payload=payload, published_at=datetime.now(UTC))


class EventBus:
    def __init__(self, subscriber_buffer_size: int = 2000, history_size: int = 200) -> None:
        self._subscriber_buffer_size = subscriber_buffer_size
        self._subscribers: set[asyncio.Queue[PublishedEvent]] = set()
        self._histories: defaultdict[History, deque[PublishedEvent]] = defaultdict(lambda: deque(maxlen=history_size))

    def publish(self, event_type: str, payload: object, *, history: History | None = None) -> PublishedEvent:
        event = PublishedEvent.create(event_type, payload)
        if history is not None:
            self._histories[history].append(event)
        for queue in self._subscribers:
            if queue.full():
                queue.get_nowait()
            queue.put_nowait(event)
        return event

    def history(self, history: History) -> list[PublishedEvent]:
        return list(self._histories[history])

    @contextmanager
    def subscribe(self) -> Iterator[asyncio.Queue[PublishedEvent]]:
        queue: asyncio.Queue[PublishedEvent] = asyncio.Queue(maxsize=self._subscriber_buffer_size)
        self._subscribers.add(queue)
        try:
            yield queue
        finally:
            self._subscribers.discard(queue)
