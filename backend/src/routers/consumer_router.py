from fastapi import APIRouter, HTTPException, status

from di.consumer_providers import (
    CommandConsumerDependency,
    CreateConsumerDependency,
    ListConsumersDependency,
    RemoveConsumerDependency,
)
from di.kernel_providers import SettingsDependency
from modules.consumer.core.entities.commands import (
    ChangeDelay,
    ConsumerCommand,
    PauseConsumption,
    ResumeConsumption,
    SeekPartition,
)
from modules.consumer.core.entities.consumer_state import ConsumerState
from modules.consumer.core.errors.consumer_errors import ConsumerNotFoundError
from modules.consumer.core.use_cases.command_consumer import CommandConsumer
from schemas.consumer_schemas import (
    CommandAcceptedResponse,
    CreateConsumerRequest,
    SeekRequest,
    UpdateConsumerRequest,
)

router = APIRouter(prefix="/consumers", tags=["consumers"])


@router.get("")
async def list_consumers(list_all: ListConsumersDependency) -> list[ConsumerState]:
    return [overview.state for overview in list_all.execute()]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_consumer(
    request: CreateConsumerRequest,
    create: CreateConsumerDependency,
    settings: SettingsDependency,
) -> ConsumerState:
    delay_ms = request.delay_ms if request.delay_ms is not None else settings.consumer_default_delay_ms
    return create.execute(request.group_id, delay_ms)


@router.delete("/{consumer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_consumer(consumer_id: str, remove: RemoveConsumerDependency) -> None:
    try:
        await remove.execute(consumer_id)
    except ConsumerNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error


@router.post("/{consumer_id}/pause", status_code=status.HTTP_202_ACCEPTED)
async def pause_consumer(consumer_id: str, command_consumer: CommandConsumerDependency) -> CommandAcceptedResponse:
    return _submit(command_consumer, consumer_id, PauseConsumption(), "pause")


@router.post("/{consumer_id}/resume", status_code=status.HTTP_202_ACCEPTED)
async def resume_consumer(consumer_id: str, command_consumer: CommandConsumerDependency) -> CommandAcceptedResponse:
    return _submit(command_consumer, consumer_id, ResumeConsumption(), "resume")


@router.patch("/{consumer_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_consumer(
    consumer_id: str,
    request: UpdateConsumerRequest,
    command_consumer: CommandConsumerDependency,
) -> CommandAcceptedResponse:
    return _submit(command_consumer, consumer_id, ChangeDelay(request.delay_ms), "delay")


@router.post("/{consumer_id}/seek", status_code=status.HTTP_202_ACCEPTED)
async def seek_consumer(
    consumer_id: str,
    request: SeekRequest,
    command_consumer: CommandConsumerDependency,
) -> CommandAcceptedResponse:
    return _submit(command_consumer, consumer_id, SeekPartition(request.partition, request.offset), "seek")


def _submit(
    command_consumer: CommandConsumer,
    consumer_id: str,
    command: ConsumerCommand,
    command_name: str,
) -> CommandAcceptedResponse:
    try:
        command_consumer.execute(consumer_id, command)
    except ConsumerNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error
    return CommandAcceptedResponse(consumer_id=consumer_id, command=command_name)
