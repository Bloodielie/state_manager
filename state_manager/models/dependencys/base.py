from abc import abstractmethod
from typing import Callable, Optional, Iterator

from pydantic import BaseModel

from state_manager.dependency.container import ExternalDependenciesContainer
from state_manager.dependency.models import DependencyWrapper
from state_manager.models.state import StateData
from state_manager.storages.base import BaseStorage
from state_manager.types import Data


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


class BaseDependencyStorage(BaseModel):
    storage: BaseStorage
    state_manager: Optional[BaseStateManager] = None
    external_dependencies: ExternalDependenciesContainer = ExternalDependenciesContainer()

    def __iter__(self) -> Iterator[DependencyWrapper]:
        for dependency in self.fields.values():
            yield DependencyWrapper(type_=dependency.type_, implementation=getattr(self, dependency.name, None))
        for dependency in self.external_dependencies:
            yield dependency

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
