from typing import Literal

from pydantic import BaseModel, Field

from modules.producer.core.entities.auto_producer_status import AutoProducerStatus
from modules.producer.core.entities.message import MessageSent, SendOutcome

MAX_RATE_PER_SEC = 50


class SendMessageRequest(BaseModel):
    key: str | None = Field(default=None, max_length=200)
    value: str = Field(min_length=1, max_length=10_000)


class StartAutoProducerRequest(BaseModel):
    rate_per_sec: float = Field(gt=0, le=MAX_RATE_PER_SEC)


class SendResultResponse(BaseModel):
    status: Literal["sent", "failed"]
    key: str | None
    partition: int | None = None
    offset: int | None = None
    latency_ms: float
    error: str | None = None

    @classmethod
    def of(cls, outcome: SendOutcome) -> "SendResultResponse":
        if isinstance(outcome, MessageSent):
            return cls(
                status="sent",
                key=outcome.key,
                partition=outcome.partition,
                offset=outcome.offset,
                latency_ms=outcome.latency_ms,
            )
        return cls(status="failed", key=outcome.key, latency_ms=outcome.latency_ms, error=outcome.error)


class AutoProducerStatusResponse(BaseModel):
    running: bool
    rate_per_sec: float

    @classmethod
    def of(cls, status: AutoProducerStatus) -> "AutoProducerStatusResponse":
        return cls(running=status.running, rate_per_sec=status.rate_per_sec)
