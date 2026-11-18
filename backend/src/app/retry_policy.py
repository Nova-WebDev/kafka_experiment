import asyncio
import logging
from collections.abc import Awaitable, Callable
from contextlib import suppress
from dataclasses import dataclass, replace
from typing import ClassVar

from app.event_bus import EventBus, History, PublishedEvent

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BackoffSchedule:
    initial_delays_seconds: tuple[float, ...]
    max_delay_seconds: float

    def delay_for(self, attempt: int) -> float:
        if attempt <= len(self.initial_delays_seconds):
            return self.initial_delays_seconds[attempt - 1]
        return self.max_delay_seconds


@dataclass(frozen=True)
class ConnectionRetry:
    event_type: ClassVar[str] = "connection.retry"

    source: str
    attempt: int
    delay_seconds: float
    error: str


@dataclass(frozen=True)
class ConnectionRestored:
    event_type: ClassVar[str] = "connection.restored"

    source: str
    failed_attempts: int


@dataclass(frozen=True)
class _PendingRetry:
    event: PublishedEvent
    retry: ConnectionRetry
    deadline: float


class ConnectionRetryPolicy:
    def __init__(self, event_bus: EventBus, schedule: BackoffSchedule) -> None:
        self._event_bus = event_bus
        self._schedule = schedule
        self._skip_signal = asyncio.Event()
        self._pending: dict[str, _PendingRetry] = {}

    async def connect[T](self, source: str, attempt_connection: Callable[[], Awaitable[T]]) -> T:
        failed_attempts = 0
        try:
            while True:
                try:
                    result = await attempt_connection()
                except Exception as error:
                    failed_attempts += 1
                    await self._wait_before_retry(source, failed_attempts, error)
                    continue
                self._mark_restored(source, failed_attempts)
                return result
        except asyncio.CancelledError:
            self._pending.pop(source, None)
            raise

    def retry_now(self) -> int:
        waiting = len(self._pending)
        self._skip_signal.set()
        self._skip_signal = asyncio.Event()
        return waiting

    def pending_retries(self) -> list[PublishedEvent]:
        now = asyncio.get_running_loop().time()
        return [
            replace(
                pending.event,
                payload=replace(pending.retry, delay_seconds=max(0.0, round(pending.deadline - now, 1))),
            )
            for pending in self._pending.values()
        ]

    async def _wait_before_retry(self, source: str, attempt: int, error: Exception) -> None:
        delay = self._schedule.delay_for(attempt)
        retry = ConnectionRetry(source=source, attempt=attempt, delay_seconds=delay, error=_describe(error))
        event = self._event_bus.publish(retry.event_type, retry, history=History.TIMELINE)
        self._pending[source] = _PendingRetry(event, retry, asyncio.get_running_loop().time() + delay)
        logger.warning("%s connection failed (attempt %d), retrying in %ss: %s", source, attempt, delay, retry.error)
        skip_signal = self._skip_signal
        with suppress(TimeoutError):
            await asyncio.wait_for(skip_signal.wait(), timeout=delay)

    def _mark_restored(self, source: str, failed_attempts: int) -> None:
        self._pending.pop(source, None)
        if failed_attempts == 0:
            return
        restored = ConnectionRestored(source=source, failed_attempts=failed_attempts)
        self._event_bus.publish(restored.event_type, restored, history=History.TIMELINE)
        logger.info("%s connection restored after %d failed attempts", source, failed_attempts)


def _describe(error: Exception) -> str:
    message = str(error)
    return f"{type(error).__name__}: {message}" if message else type(error).__name__
