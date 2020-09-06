from abc import abstractmethod
from typing import Callable, Optional

from pydantic import BaseModel

from state_manager.models.state import StateData
from state_manager.storages.base import BaseStorage
from state_manager.types.generals import Data


class Depends:
    def __init__(self, dependency: Callable) -> None:
        self.dependency = dependency

    def __repr__(self) -> str:
        attr = getattr(self.dependency, "__name__", type(self.dependency).__name__)
        return f"{self.__class__.__name__}({attr})"


class BaseStateManager(BaseModel):
    storage: BaseStorage

    async def set_next_state(self, state_name: str, *, data: Data = None) -> None:
        raise NotImplementedError

    async def back_to_pre_state(self, *, data: Data = None) -> None:
        raise NotImplementedError

    @property
    async def data(self) -> Optional[Data]:
        data = await self._get_state_data()
        return data.data if data is not None else None

    @property
    async def current_state(self) -> Optional[str]:
        data = await self._get_state_data()
        return data.current_state if data is not None else None

    @property
    async def pre_state(self) -> Optional[str]:
        data = await self._get_state_data()
        return data.pre_state if data is not None else None

    @property
    async def state_data(self) -> Optional[StateData]:
        return await self._get_state_data()

    @abstractmethod
    async def _get_state_data(self) -> Optional[StateData]:
        pass

    class Config:
        arbitrary_types_allowed = True


async def back_to_pre_state_(storage: BaseStorage, user_id: str, data: Data) -> None:
    state = await storage.get(user_id)
    if state is None:
        raise ValueError("Type of state not supported")
    if state.pre_state is None:
        state_data = StateData(current_state=state.current_state, data=data)
    else:
        state_data = StateData(current_state=state.pre_state, data=data)
    await storage.put(user_id, state_data)
