from typing import TypeVar, Generic, Set

from pydantic.generics import GenericModel

from state_manager.storages.state_storage import StateStorage

BaseRouters = TypeVar("BaseRouters")


class RouterStorage(GenericModel, Generic[BaseRouters]):
    state_storage: StateStorage
    routers: Set[BaseRouters] = set()

    class Config:
        arbitrary_types_allowed = True
