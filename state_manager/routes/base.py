from abc import ABC, abstractmethod
from logging import getLogger
from typing import Callable, Optional, Set, Tuple, Union, List

from state_manager.dependency.container import ExternalDependenciesContainer
from state_manager.models.routers_storage import RouterStorage
from state_manager.models.state import StateModel
from state_manager.storages.base import BaseStorage
from state_manager.storages.state_storage import StateStorage

logger = getLogger(__name__)


class BaseRouter(ABC):
    def __init__(self, routers: Optional[Union[List["BaseRouter"], Set["BaseRouter"]]] = None) -> None:
        if isinstance(routers, list) or isinstance(routers, tuple):
            routers = set(routers)
        else:
            routers = set()
        self.storage = RouterStorage[BaseRouter](state_storage=StateStorage(), routers=routers)

    def registration_state_handler(
        self,
        event_type: str,
        handler: Callable,
        *,
        state_name: Optional[Union[str, list, tuple]] = None,
        filters: Optional[Tuple[Callable[..., bool], ...]] = None,
    ) -> None:
        if isinstance(state_name, str) or state_name is None:
            state_names = [state_name]
        else:
            state_names = state_name
        logger.debug(f"registration_state_handler, {event_type=}, {handler=}, {state_names=}, {filters=}")
        if isinstance(filters, tuple) and (len(filters) == 0):
            filters = None
        for state_name in state_names:
            state_name = state_name or handler.__name__
            state = StateModel(name=state_name, event_type=event_type, handler=handler, filters=filters)
            self.storage.state_storage.add_state(state)

    def include_router(self, router: "BaseRouter") -> None:
        logger.debug(f"include_router, {router=}")
        self.storage.routers.bind(router)


class BaseMainRouter(BaseRouter):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.external_dependencies = ExternalDependenciesContainer()

    @abstractmethod
    def install(
        self,
        *,
        storage: Optional[BaseStorage] = None,
        default_state_name: Optional[str] = None,
        is_cached: bool = True,
    ) -> None:
        ...
