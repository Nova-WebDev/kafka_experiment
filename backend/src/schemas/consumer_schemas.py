from pydantic import BaseModel, Field
from sse_starlette import ServerSentEvent

from modules.consumer.core.entities.consumer_overview import ConsumerOverview
from modules.consumer.core.entities.consumer_state import ConsumerState
from schemas.event_schemas import EventEnvelope

MAX_DELAY_MS = 5000
CONSUMERS_SNAPSHOT_EVENT = "consumers.snapshot"


class CreateConsumerRequest(BaseModel):
    group_id: str | None = Field(default=None, min_length=1, max_length=120)
    delay_ms: int | None = Field(default=None, ge=0, le=MAX_DELAY_MS)


class UpdateConsumerRequest(BaseModel):
    delay_ms: int = Field(ge=0, le=MAX_DELAY_MS)


class SeekRequest(BaseModel):
    partition: int = Field(ge=0)
    offset: int = Field(ge=0)


class CommandAcceptedResponse(BaseModel):
    consumer_id: str
    command: str


class ConsumerOverviewSchema(BaseModel):
    state: ConsumerState
    messages: list[EventEnvelope]


class ConsumersSnapshot(BaseModel):
    consumers: list[ConsumerOverviewSchema]


def consumers_snapshot_event(overviews: list[ConsumerOverview]) -> ServerSentEvent:
    snapshot = ConsumersSnapshot(
        consumers=[
            ConsumerOverviewSchema(
                state=overview.state,
                messages=[EventEnvelope.of(message) for message in overview.recent_messages],
            )
            for overview in overviews
        ]
    )
    return ServerSentEvent(event=CONSUMERS_SNAPSHOT_EVENT, data=snapshot.model_dump_json())
