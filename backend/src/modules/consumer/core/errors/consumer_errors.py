class ConsumerError(Exception):
    pass


class ConsumerNotFoundError(ConsumerError):
    def __init__(self, consumer_id: str) -> None:
        super().__init__(f"Consumer {consumer_id} not found")
        self.consumer_id = consumer_id


class ConsumerConnectionError(ConsumerError):
    pass


class OffsetCommitError(ConsumerError):
    pass
