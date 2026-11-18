from dataclasses import dataclass


@dataclass(frozen=True)
class ConsumerTuning:
    fetch_timeout_ms: int
    watermark_refresh_seconds: float
    broker_call_timeout_seconds: float
    recent_messages_limit: int
