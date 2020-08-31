from typing import TypeVar, Generic, Set, Callable, Optional, Tuple, Union

from pydantic.generics import GenericModel
from pydantic import BaseModel

from state_manager.filters.base import BaseFilter
from state_manager.storages.state_storage import StateStorage

BaseRouters = TypeVar("BaseRouters")


class RouterStorage(GenericModel, Generic[BaseRouters]):
    state_storage: StateStorage
    routers: Set[BaseRouters] = set()

    class Config:
        arbitrary_types_allowed = True


class HandlerStorage(BaseModel):
    handler: Callable
    filters: Optional[Tuple[Union[Callable, BaseFilter]]] = None

    class Config:
        arbitrary_types_allowed = True
