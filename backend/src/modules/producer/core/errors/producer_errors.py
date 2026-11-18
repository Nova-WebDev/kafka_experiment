class ProducerError(Exception):
    pass


class MessageDeliveryError(ProducerError):
    def __init__(self, error_name: str) -> None:
        super().__init__(error_name)
        self.error_name = error_name


class ProducerNotConnectedError(MessageDeliveryError):
    def __init__(self) -> None:
        super().__init__("ProducerNotConnected")
