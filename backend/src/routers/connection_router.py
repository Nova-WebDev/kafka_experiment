from fastapi import APIRouter

from di.kernel_providers import RetryPolicyDependency
from schemas.connection_schemas import RetryNowResponse

router = APIRouter(prefix="/connection", tags=["connection"])


@router.post("/retry-now")
async def retry_now(retry_policy: RetryPolicyDependency) -> RetryNowResponse:
    return RetryNowResponse(skipped_waits=retry_policy.retry_now())
