import typing
from abc import abstractmethod

from state_manager.models.state import StateData


@typing.runtime_checkable
class BaseStorage(typing.Protocol):
    @abstractmethod
    async def get(self, key: str, default: typing.Optional[StateData] = None) -> typing.Optional[StateData]:
        raise NotImplementedError

    @abstractmethod
    async def put(self, key: str, value: StateData) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> typing.Optional[typing.NoReturn]:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError
