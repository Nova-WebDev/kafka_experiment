class ClusterError(Exception):
    pass


class ClusterUnavailableError(ClusterError):
    pass


class TopicAlreadyExistsError(ClusterError):
    pass


class TopicOperationError(ClusterError):
    pass
