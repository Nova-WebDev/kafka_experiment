from abc import ABC, abstractmethod

from modules.cluster.core.entities.broker import BrokerAddress


class BrokerProbe(ABC):
    @abstractmethod
    async def is_reachable(self, address: BrokerAddress) -> bool: ...
