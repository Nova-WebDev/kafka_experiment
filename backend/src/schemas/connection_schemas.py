from pydantic import BaseModel


class RetryNowResponse(BaseModel):
    skipped_waits: int
