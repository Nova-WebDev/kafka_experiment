from app.retry_policy import ConnectionRetryPolicy
from modules.producer.core.interfaces.message_publisher import MessagePublisher

CONNECTION_SOURCE = "producer"


class ConnectProducer:
    def __init__(self, publisher: MessagePublisher, retry_policy: ConnectionRetryPolicy) -> None:
        self._publisher = publisher
        self._retry_policy = retry_policy

    async def execute(self) -> None:
        await self._retry_policy.connect(CONNECTION_SOURCE, self._publisher.start)
