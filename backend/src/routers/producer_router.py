from fastapi import APIRouter, Response, status

from di.producer_providers import AutoProducerDependency, SendMessageDependency, SendOrderDependency
from modules.producer.core.entities.message import MessageFailed, OutgoingMessage, SendOutcome, SendSource
from schemas.producer_schemas import (
    AutoProducerStatusResponse,
    SendMessageRequest,
    SendResultResponse,
    StartAutoProducerRequest,
)

router = APIRouter(prefix="/producer", tags=["producer"])


@router.post("/messages")
async def send_message(
    request: SendMessageRequest,
    response: Response,
    send: SendMessageDependency,
) -> SendResultResponse:
    outcome = await send.execute(OutgoingMessage(key=request.key or None, value=request.value), SendSource.MANUAL)
    return _respond(outcome, response)


@router.post("/orders")
async def send_order(response: Response, send: SendOrderDependency) -> SendResultResponse:
    return _respond(await send.execute(SendSource.MANUAL), response)


@router.post("/auto/start")
async def start_auto_producer(
    request: StartAutoProducerRequest,
    auto_producer: AutoProducerDependency,
) -> AutoProducerStatusResponse:
    return AutoProducerStatusResponse.of(await auto_producer.start(request.rate_per_sec))


@router.post("/auto/stop")
async def stop_auto_producer(auto_producer: AutoProducerDependency) -> AutoProducerStatusResponse:
    return AutoProducerStatusResponse.of(await auto_producer.stop())


def _respond(outcome: SendOutcome, response: Response) -> SendResultResponse:
    if isinstance(outcome, MessageFailed):
        response.status_code = status.HTTP_502_BAD_GATEWAY
    return SendResultResponse.of(outcome)
