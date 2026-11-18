from dataclasses import dataclass


@dataclass(frozen=True)
class PartitionState:
    partition: int
    leader: int | None
    replicas: tuple[int, ...]
    isr: tuple[int, ...]

    def live_isr(self, reachable_broker_ids: frozenset[int]) -> tuple[int, ...]:
        return tuple(broker_id for broker_id in self.isr if broker_id in reachable_broker_ids)

    def accepts_writes(self, reachable_broker_ids: frozenset[int], min_insync_replicas: int) -> bool:
        leader_alive = self.leader is not None and self.leader in reachable_broker_ids
        return leader_alive and len(self.live_isr(reachable_broker_ids)) >= min_insync_replicas
