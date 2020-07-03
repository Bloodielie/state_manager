from typing import Callable, Optional, Set, Type, Tuple

from aiogram import Dispatcher

from state_manager.filter import BaseFilter
from state_manager.middleware import StateMiddleware
from state_manager.models.state import StateModel
from state_manager.storage.base import BaseStorage
from state_manager.storage.state_storage import StateStorage


# todo: add support inline handler and other handlers
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
        filters: Optional[Tuple[Type[BaseFilter]]] = None
    ) -> None:
        if isinstance(filters, tuple) and (len(filters) == 0):
            filters = None
        state_name = state_name or handler.__name__
        state = StateModel(name=state_name, event_type=event_type, handler=handler, filters=filters)
        self.state_storage.add_state(state)

    def include_router(self, router: "StateRouter") -> None:
        self.routers.add(router)

    def message_handler(self, *filters: Type[BaseFilter], state_name: Optional[str] = None) -> Callable:
        def wrap(callback: Callable):
            self.registration_state_handler("message", callback, state_name=state_name, filters=filters)
            return callback

        return wrap

    def callback_query_handler(self, *filters: Type[BaseFilter], state_name: Optional[str] = None) -> Callable:
        def wrap(callback: Callable):
            self.registration_state_handler("callback_query", callback, state_name=state_name, filters=filters)
            return callback

        return wrap


class MainStateRouter(StateRouter):
    def __init__(self, dispatcher: Optional[Dispatcher] = None) -> None:
        super().__init__()
        self.dispatcher = dispatcher or Dispatcher.get_current()

    def install_middleware(
        self, *, storage: Optional[Type[BaseStorage]] = None, default_state_name: Optional[str] = None
    ) -> None:
        self.dispatcher.middleware.setup(StateMiddleware(self, storage=storage, default_state_name=default_state_name))
