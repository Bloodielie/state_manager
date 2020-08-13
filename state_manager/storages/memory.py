import typing
from logging import getLogger

from state_manager import BaseStorage
from state_manager.models.state import StateData

logger = getLogger(__name__)


class MemoryStorage(BaseStorage):
    def __init__(self):
        self.data = {}

    async def close(self) -> None:
        self.data.clear()

    async def get(self, key: str, default: typing.Optional[StateData] = None) -> typing.Optional[StateData]:
        logger.debug(f"get, key={key}, default={default}")
        key_ = self.data.get(key)
        if key_:
            return StateData.parse_raw(key_)
        return default

    async def put(self, key: str, value: StateData) -> None:
        logger.debug(f"put, key={key}, value={value}")
        pre_state = await self.get(key)
        if pre_state is not None:
            value.pre_state = pre_state.current_state
            self.data[key] = value.json()
        self.data[key] = value.json()

    async def delete(self, key: str) -> None:
        logger.debug(f"delete, key={key}")
        if not await self.contains(key):
            raise KeyError("Storage doesn't contain this key.")
        del self.data[key]

    async def contains(self, key: str) -> bool:
        logger.debug(f"contains, key={key}")
        return True if self.data.get(key) else False
