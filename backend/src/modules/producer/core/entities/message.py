from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar


class SendSource(StrEnum):
    MANUAL = "manual"
    AUTO = "auto"


@dataclass(frozen=True)
class OutgoingMessage:
    key: str | None
    value: str


@dataclass(frozen=True)
class DeliveryReceipt:
    partition: int
    offset: int


@dataclass(frozen=True)
class MessageSent:
    event_type: ClassVar[str] = "producer.sent"

    source: SendSource
    key: str | None
    value: str
    partition: int
    offset: int
    latency_ms: float


@dataclass(frozen=True)
class MessageFailed:
    event_type: ClassVar[str] = "producer.failed"

    source: SendSource
    key: str | None
    value: str
    error: str
    latency_ms: float


SendOutcome = MessageSent | MessageFailed
