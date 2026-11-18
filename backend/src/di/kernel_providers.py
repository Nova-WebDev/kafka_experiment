from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.event_bus import EventBus
from app.retry_policy import BackoffSchedule, ConnectionRetryPolicy
from app.settings import Settings


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_event_bus() -> EventBus:
    return EventBus()


@lru_cache
def get_retry_policy() -> ConnectionRetryPolicy:
    settings = get_settings()
    schedule = BackoffSchedule(
        initial_delays_seconds=settings.retry_initial_delays_seconds,
        max_delay_seconds=settings.retry_max_delay_seconds,
    )
    return ConnectionRetryPolicy(get_event_bus(), schedule)


SettingsDependency = Annotated[Settings, Depends(get_settings)]
EventBusDependency = Annotated[EventBus, Depends(get_event_bus)]
RetryPolicyDependency = Annotated[ConnectionRetryPolicy, Depends(get_retry_policy)]
