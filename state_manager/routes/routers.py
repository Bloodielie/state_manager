from aiogram import Dispatcher
from typing import Callable, Optional, Set

from state_manager.middleware import StateMiddleware
from state_manager.models.state import StateModel
from state_manager.storage.base import BaseStorage
from state_manager.storage.state_storage import StateStorage


class StateRouter:
    def __init__(self) -> None:
        self.state_storage = StateStorage()
        self.routers: Set["StateRouter"] = set()

    def registration_state_handler(
        self,
        event_type: str,
        handler: Callable,
        *,
        state_name: Optional[str] = None,
        filter: Optional[Callable] = None
    ) -> None:
        state_name = state_name or handler.__name__
        state = StateModel(name=state_name, event_type=event_type, handler=handler, filter=filter)
        self.state_storage.add_state(state)

    def include_router(self, router: "StateRouter") -> None:
        self.routers.add(router)

    def message_handler(self, *, state_name: Optional[str] = None) -> Callable:
        def wrap(callback: Callable):
            self.registration_state_handler("message", callback, state_name=state_name)
            return callback

        return wrap

    def callback_query_handler(self, *, state_name: Optional[str] = None) -> Callable:
        def wrap(callback: Callable):
            self.registration_state_handler("callback_query", callback, state_name=state_name)
            return callback

        return wrap


class MainStateRouter(StateRouter):
    def __init__(self, dispatcher: Optional[Dispatcher] = None) -> None:
        super().__init__()
        self.dispatcher = dispatcher or Dispatcher.get_current()

    def install_middleware(
        self, *, storage: Optional[BaseStorage] = None, default_state_name: Optional[str] = None
    ) -> None:
        self.dispatcher.middleware.setup(
            StateMiddleware(self, storage=storage, default_state_name=default_state_name)
        )
