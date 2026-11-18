import asyncio
from contextlib import suppress

from modules.cluster.core.entities.broker import BrokerAddress
from modules.cluster.core.interfaces.broker_probe import BrokerProbe


class TcpBrokerProbe(BrokerProbe):
    def __init__(self, timeout_seconds: float) -> None:
        self._timeout_seconds = timeout_seconds

    async def is_reachable(self, address: BrokerAddress) -> bool:
        try:
            async with asyncio.timeout(self._timeout_seconds):
                _, writer = await asyncio.open_connection(address.host, address.port)
        except (OSError, TimeoutError):
            return False
        writer.close()
        with suppress(OSError):
            await writer.wait_closed()
        return True
