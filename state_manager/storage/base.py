import typing
from abc import ABC, abstractmethod


class BaseStorage(ABC):
    @abstractmethod
    async def get(self, key: str, default: typing.Optional[typing.Any] = None) -> typing.Union[None, typing.Any]:
        raise NotImplementedError

    @abstractmethod
    async def put(self, key: str, value: typing.Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> typing.Optional[typing.NoReturn]:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError
