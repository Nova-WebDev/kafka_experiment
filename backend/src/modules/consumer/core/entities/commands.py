from dataclasses import dataclass


@dataclass(frozen=True)
class PauseConsumption:
    pass


@dataclass(frozen=True)
class ResumeConsumption:
    pass


@dataclass(frozen=True)
class SeekPartition:
    partition: int
    offset: int


@dataclass(frozen=True)
class ChangeDelay:
    delay_ms: int


ConsumerCommand = PauseConsumption | ResumeConsumption | SeekPartition | ChangeDelay
