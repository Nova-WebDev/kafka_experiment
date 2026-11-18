from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class AutoProducerStatus:
    event_type: ClassVar[str] = "producer.auto"

    running: bool
    rate_per_sec: float
