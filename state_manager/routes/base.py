from abc import ABC, abstractmethod
from logging import getLogger
from typing import Callable, Optional, Set, Union, List, Any

from state_manager.dependency.container import AppContainer
from state_manager.models.events import EventsModel
from state_manager.storages.app import RouterStorage
from state_manager.models.state import StateModel
from state_manager.storages.base import BaseStorage
from state_manager.storages.state_storage import StateStorage
from state_manager.types.generals import Filters, StateNames

try:
    from aiogram.types.base import TelegramObject as context
except ImportError:
    from vkwave.bots import BaseEvent as context

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
        self.container = AppContainer([context])

    @abstractmethod
    def install(
        self,
        *,
        storage: Optional[BaseStorage] = None,
        default_state_name: Optional[str] = None
    ) -> None:
        ...


class BaseRouter(ABC):
    def __init__(self) -> None:
        self._state_storage = StateStorage()

    def include_router(self, router: "BaseRouter") -> None:
        logger.debug(f"include_router, router={router}")
        self._state_storage.expand(router._state_storage)


class BaseMainRouter(BaseRouter):
    def __init__(self, token: str):
        self.token = token
        self.container = AppContainer([context])
        self._events = EventsModel()
        super().__init__()

    @abstractmethod
    def install(
        self, *, storage: Optional[BaseStorage] = None, default_state_name: Optional[str] = None
    ) -> None:
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    def on_startup(self, func: Callable[..., Any]) -> None:
        self._events.on_startup = func

    def on_shutdown(self, func: Callable[..., Any]) -> None:
        self._events.on_shutdown = func

    def run(
        self,
        *,
        storage: Optional[BaseStorage] = None,
        default_state_name: Optional[str] = None,
        on_startup: Optional[Callable[..., Any]] = None,
        on_shutdown: Optional[Callable[..., Any]] = None,
    ) -> None:
        logger.debug(f"run main_router, storage={storage}, default_state_name={default_state_name}")
        if on_startup is not None:
            self.on_startup(on_startup)
        if on_shutdown is not None:
            self.on_shutdown(on_shutdown)

        self.install(storage=storage, default_state_name=default_state_name)
        self.start()
