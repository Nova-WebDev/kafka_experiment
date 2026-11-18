from collections.abc import AsyncIterator

from fastapi import APIRouter
from sse_starlette import EventSourceResponse, ServerSentEvent

from app.event_bus import History, PublishedEvent
from di.cluster_providers import ClusterMonitorDependency
from di.consumer_providers import ListConsumersDependency
from di.kernel_providers import EventBusDependency, RetryPolicyDependency, SettingsDependency
from di.producer_providers import AutoProducerDependency
from schemas.consumer_schemas import consumers_snapshot_event
from schemas.event_schemas import history_event, to_server_sent_event

router = APIRouter(tags=["events"])


@router.get("/events")
async def stream_events(
    *,
    event_bus: EventBusDependency,
    monitor: ClusterMonitorDependency,
    retry_policy: RetryPolicyDependency,
    auto_producer: AutoProducerDependency,
    list_consumers: ListConsumersDependency,
    settings: SettingsDependency,
) -> EventSourceResponse:
    async def event_stream() -> AsyncIterator[ServerSentEvent]:
        with event_bus.subscribe() as queue:
            snapshot = monitor.current_snapshot()
            if snapshot is not None:
                yield to_server_sent_event(PublishedEvent.create(snapshot.event_type, snapshot))
            yield consumers_snapshot_event(list_consumers.execute())
            yield history_event(History.TIMELINE, event_bus.history(History.TIMELINE))
            yield history_event(History.PRODUCER, event_bus.history(History.PRODUCER))
            auto_status = auto_producer.status()
            yield to_server_sent_event(PublishedEvent.create(auto_status.event_type, auto_status))
            for pending_retry in retry_policy.pending_retries():
                yield to_server_sent_event(pending_retry)
            while True:
                yield to_server_sent_event(await queue.get())

    return EventSourceResponse(
        event_stream(),
        ping=settings.sse_heartbeat_seconds,
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
