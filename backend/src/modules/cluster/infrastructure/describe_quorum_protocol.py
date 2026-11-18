from aiokafka.protocol.api import Request, RequestStruct, Response
from aiokafka.protocol.types import CompactArray, CompactString, Int16, Int32, Int64, Schema

DESCRIBE_QUORUM_API_KEY = 55
METADATA_LOG_TOPIC = "__cluster_metadata"
METADATA_LOG_PARTITION = 0
NO_LEADER = -1

_REPLICA_STATE = Schema(
    ("replica_id", Int32),
    ("log_end_offset", Int64),
    tagged_fields=(),
)


class DescribeQuorumResponseV0(Response):
    API_KEY = DESCRIBE_QUORUM_API_KEY
    API_VERSION = 0
    SCHEMA = Schema(
        ("error_code", Int16),
        (
            "topics",
            CompactArray(
                Schema(
                    ("topic_name", CompactString("utf-8")),
                    (
                        "partitions",
                        CompactArray(
                            Schema(
                                ("partition_index", Int32),
                                ("error_code", Int16),
                                ("leader_id", Int32),
                                ("leader_epoch", Int32),
                                ("high_watermark", Int64),
                                ("current_voters", CompactArray(_REPLICA_STATE)),
                                ("observers", CompactArray(_REPLICA_STATE)),
                                tagged_fields=(),
                            )
                        ),
                    ),
                    tagged_fields=(),
                )
            ),
        ),
        tagged_fields=(),
    )


class DescribeQuorumRequestV0(RequestStruct):
    API_KEY = DESCRIBE_QUORUM_API_KEY
    API_VERSION = 0
    RESPONSE_TYPE = DescribeQuorumResponseV0
    SCHEMA = Schema(
        (
            "topics",
            CompactArray(
                Schema(
                    ("topic_name", CompactString("utf-8")),
                    ("partitions", CompactArray(Schema(("partition_index", Int32), tagged_fields=()))),
                    tagged_fields=(),
                )
            ),
        ),
        tagged_fields=(),
    )


class DescribeQuorumRequest(Request[DescribeQuorumRequestV0]):
    API_KEY = DESCRIBE_QUORUM_API_KEY

    def build(self, request_struct_class: type[DescribeQuorumRequestV0]) -> DescribeQuorumRequestV0:
        return request_struct_class([(METADATA_LOG_TOPIC, [(METADATA_LOG_PARTITION,)])])


def quorum_leader_id(response: DescribeQuorumResponseV0) -> int | None:
    payload = response.to_object()
    if payload["error_code"] != 0:
        return None
    for topic in payload["topics"]:
        for partition in topic["partitions"]:
            if partition["error_code"] == 0 and partition["leader_id"] != NO_LEADER:
                return partition["leader_id"]
    return None
