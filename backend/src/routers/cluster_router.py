from fastapi import APIRouter, HTTPException, status

from di.cluster_providers import ClusterMonitorDependency, ResetTopicDependency
from di.consumer_providers import RemoveConsumerDependency
from modules.cluster.core.entities.cluster_snapshot import ClusterSnapshot
from modules.cluster.core.errors.cluster_errors import ClusterUnavailableError, TopicOperationError
from schemas.topic_schemas import TopicResetResponse

router = APIRouter(tags=["cluster"])


@router.get("/cluster")
async def get_cluster_snapshot(monitor: ClusterMonitorDependency) -> ClusterSnapshot:
    snapshot = monitor.current_snapshot()
    if snapshot is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "No cluster snapshot yet")
    return snapshot


@router.post("/topic/reset")
async def reset_topic(reset: ResetTopicDependency, remove_consumer: RemoveConsumerDependency) -> TopicResetResponse:
    await remove_consumer.execute_for_all()
    try:
        return TopicResetResponse.of(await reset.execute())
    except ClusterUnavailableError as error:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(error)) from error
    except TopicOperationError as error:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(error)) from error
