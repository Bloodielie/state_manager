from abc import ABC, abstractmethod
from typing import Optional, Union, List, Set, Callable

from pyject import Container

from state_manager import BaseStorage
from state_manager.models.state import StateModel
from state_manager.storages.state_storage import StateStorage
from state_manager.types.generals import StateNames, Filters
from logging import getLogger

logger = getLogger(__name__)


class BaseStateRouter(ABC):
    def __init__(self, routers: Optional[Union[List["BaseStateRouter"], Set["BaseStateRouter"]]] = None) -> None:
        self._state_storage = StateStorage()

        routers = routers or []
        for router in routers:
            self.include_router(router)

    def registration_state_handler(
        self,
        event_type: str,
        handler: Callable,
        *,
        state_name: StateNames = None,
        filters: Filters = None,
    ) -> None:
        if isinstance(state_name, str) or state_name is None:
            state_names = [state_name]
        else:
            state_names = state_name
        logger.debug(
            f"registration_state_handler, event_type={event_type}, handler={handler}, state_names={state_names}, filters={filters}"
        )
        if isinstance(filters, tuple) and (len(filters) == 0):
            filters = None
        for state_name in state_names:
            state_name = state_name or handler.__name__
            state = StateModel(name=state_name, event_type=event_type, handler=handler, filters=filters)
            self._state_storage.add_state(state)

    def include_router(self, router: "BaseStateRouter") -> None:
        logger.debug(f"include_router, router={router}")
        self._state_storage.expand(router._state_storage)


class BaseMainStateRouter(BaseStateRouter):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.container = Container()

    @abstractmethod
    def install(
        self,
        *,
        storage: Optional[BaseStorage] = None,
        default_state_name: Optional[str] = None
    ) -> None:
        ...
