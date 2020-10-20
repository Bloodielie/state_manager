from abc import ABC, abstractmethod
from typing import Optional, Callable, Any

from pyject import Container

from state_manager import BaseStorage
from state_manager.models.events import EventsModel
from state_manager.storages.state_storage import StateStorage
from logging import getLogger

logger = getLogger(__name__)


class BaseRouter(ABC):
    def __init__(self) -> None:
        self._state_storage = StateStorage()

    def include_router(self, router: "BaseRouter") -> None:
        logger.debug(f"include_router, router={router}")
        self._state_storage.expand(router._state_storage)


class BaseMainRouter(BaseRouter):
    def __init__(self, token: str):
        self.token = token
        self.container = Container()
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
