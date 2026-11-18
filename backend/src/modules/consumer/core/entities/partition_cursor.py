from dataclasses import dataclass

from modules.consumer.core.entities.consumer_state import PartitionProgress


@dataclass
class PartitionCursor:
    partition: int
    position: int | None = None
    committed: int | None = None
    high_watermark: int | None = None
    log_start: int = 0

    def clamp(self, offset: int) -> int:
        upper = self.high_watermark if self.high_watermark is not None else offset
        return max(self.log_start, min(offset, upper))

    def to_progress(self) -> PartitionProgress:
        return PartitionProgress(
            partition=self.partition,
            position=self.position,
            committed=self.committed,
            high_watermark=self.high_watermark,
            lag=self._lag(),
        )

    def _lag(self) -> int | None:
        if self.high_watermark is None:
            return None
        consumed_up_to = next(
            (offset for offset in (self.committed, self.position) if offset is not None),
            self.log_start,
        )
        return max(0, self.high_watermark - consumed_up_to)
