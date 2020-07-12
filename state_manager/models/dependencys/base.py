from typing import Callable, Optional

from pydantic import BaseModel

from state_manager.models.state import StateData
from state_manager.storage.base import BaseStorage
from abc import abstractmethod

from state_manager.types import Data


class Depends:
    def __init__(self, dependency: Callable) -> None:
        self.dependency = dependency

    def __repr__(self) -> str:
        attr = getattr(self.dependency, "__name__", type(self.dependency).__name__)
        return f"{self.__class__.__name__}({attr})"


class BaseStateManager(BaseModel):
    storage: BaseStorage

    @abstractmethod
    async def set_next_state(self, state_name: str, *, data: Data = None) -> None:
        pass

    @abstractmethod
    async def back_to_pre_state(self, *, data: Data = None) -> None:
        pass

    @abstractmethod
    async def get_data(self) -> Data:
        pass

    @abstractmethod
    async def get_storage(self) -> StateData:
        pass

    class Config:
        arbitrary_types_allowed = True


class BaseDependencyStorage(BaseModel):
    storage: BaseStorage
    state_manager: Optional[BaseStateManager] = None

    class Config:
        arbitrary_types_allowed = True


async def back_to_pre_state_(storage: BaseStorage, user_id: str, data: Optional[dict]) -> None:
    state = await storage.get(user_id)
    if state.pre_state is None:
        state_data = StateData(current_state=state.current_state, data=data)
    else:
        state_data = StateData(current_state=state.pre_state, data=data)
    await storage.put(user_id, state_data)
