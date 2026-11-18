import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI

from app.logging_config import configure_logging
from di.cluster_providers import get_cluster_gateway, get_cluster_monitor
from di.consumer_providers import get_remove_consumer
from di.kernel_providers import get_settings
from di.producer_providers import get_auto_producer, get_connect_producer, get_message_publisher
from routers import (
    cluster_router,
    connection_router,
    consumer_router,
    events_router,
    health_router,
    producer_router,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging(get_settings().log_level)
    background_tasks = [
        asyncio.create_task(get_cluster_monitor().run(), name="cluster-monitor"),
        asyncio.create_task(get_connect_producer().execute(), name="producer-connect"),
    ]
    yield
    await get_remove_consumer().execute_for_all()
    await get_auto_producer().stop()
    for task in background_tasks:
        task.cancel()
    for task in background_tasks:
        with suppress(asyncio.CancelledError):
            await task
    await get_message_publisher().stop()
    await get_cluster_gateway().close()


app = FastAPI(title="Kafka Lab", lifespan=lifespan)
app.include_router(health_router.router)
app.include_router(cluster_router.router)
app.include_router(connection_router.router)
app.include_router(producer_router.router)
app.include_router(consumer_router.router)
app.include_router(events_router.router)
