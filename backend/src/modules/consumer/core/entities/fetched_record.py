from dataclasses import dataclass


@dataclass(frozen=True)
class FetchedRecord:
    partition: int
    offset: int
    key: str | None
    value: str
    timestamp_ms: int
