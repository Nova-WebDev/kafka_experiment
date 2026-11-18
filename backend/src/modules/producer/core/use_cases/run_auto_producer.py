import asyncio
from contextlib import suppress

from app.event_bus import EventBus
from modules.producer.core.entities.auto_producer_status import AutoProducerStatus
from modules.producer.core.entities.message import SendSource
from modules.producer.core.use_cases.send_order import SendOrder


class RunAutoProducer:
    def __init__(self, send_order: SendOrder, event_bus: EventBus, max_in_flight: int = 100) -> None:
        self._send_order = send_order
        self._event_bus = event_bus
        self._in_flight_slots = asyncio.Semaphore(max_in_flight)
        self._in_flight: set[asyncio.Task[object]] = set()
        self._loop_task: asyncio.Task[None] | None = None
        self._status = AutoProducerStatus(running=False, rate_per_sec=0)

    def status(self) -> AutoProducerStatus:
        return self._status

    async def start(self, rate_per_sec: float) -> AutoProducerStatus:
        await self._cancel_loop()
        self._loop_task = asyncio.create_task(self._produce_at(rate_per_sec), name="auto-producer")
        return self._publish_status(AutoProducerStatus(running=True, rate_per_sec=rate_per_sec))

    async def stop(self) -> AutoProducerStatus:
        await self._cancel_loop()
        return self._publish_status(AutoProducerStatus(running=False, rate_per_sec=self._status.rate_per_sec))

    async def _produce_at(self, rate_per_sec: float) -> None:
        loop = asyncio.get_running_loop()
        interval = 1 / rate_per_sec
        next_send_at = loop.time()
        while True:
            await self._in_flight_slots.acquire()
            task = asyncio.create_task(self._send_order.execute(SendSource.AUTO))
            self._in_flight.add(task)
            task.add_done_callback(self._release_slot)
            next_send_at = max(next_send_at + interval, loop.time())
            await asyncio.sleep(next_send_at - loop.time())

    def _release_slot(self, task: asyncio.Task[object]) -> None:
        self._in_flight.discard(task)
        self._in_flight_slots.release()

    async def _cancel_loop(self) -> None:
        loop_task, self._loop_task = self._loop_task, None
        if loop_task is None:
            return
        loop_task.cancel()
        with suppress(asyncio.CancelledError):
            await loop_task

    def _publish_status(self, status: AutoProducerStatus) -> AutoProducerStatus:
        self._status = status
        self._event_bus.publish(status.event_type, status)
        return status
