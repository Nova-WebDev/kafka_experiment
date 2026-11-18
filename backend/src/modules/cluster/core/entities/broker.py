from dataclasses import dataclass


@dataclass(frozen=True)
class BrokerAddress:
    broker_id: int
    host: str
    port: int


@dataclass(frozen=True)
class BrokerState:
    broker_id: int
    host: str
    reachable: bool
    in_metadata: bool
    is_controller: bool
    leader_count: int
