from typing import Callable, Optional, Set, Tuple, Any, Type

from state_manager.models.state import StateModel
from state_manager.storage.base import BaseStorage
from state_manager.storage.state_storage import StateStorage
from abc import ABC, abstractmethod


class BaseRouter(ABC):
    def __init__(self) -> None:
        self.state_storage = StateStorage()
        self.routers: Set["StateRouter"] = set()

    def registration_state_handler(
        self,
        event_type: str,
        handler: Callable,
        *,
        state_name: Optional[str] = None,
        filters: Optional[Tuple[Callable[[Any], bool]]] = None
    ) -> None:
        if isinstance(filters, tuple) and (len(filters) == 0):
            filters = None
        state_name = state_name or handler.__name__
        state = StateModel(name=state_name, event_type=event_type, handler=handler, filters=filters)
        self.state_storage.add_state(state)

    def include_router(self, router: "StateRouter") -> None:
        self.routers.add(router)


class BaseMainRouter(BaseRouter):
    @abstractmethod
    def install_middleware(
        self,
        *,
        storage: Optional[Type[BaseStorage]] = None,
        default_state_name: Optional[str] = None,
        is_cached: bool = True
    ) -> None:
        pass
