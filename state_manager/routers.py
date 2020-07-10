from typing import Callable, Optional, Set, Type, Tuple, Any

from aiogram import Dispatcher

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
        filters: Optional[Tuple[Callable[[Any], bool]]] = None
    ) -> None:
        if isinstance(filters, tuple) and (len(filters) == 0):
            filters = None
        state_name = state_name or handler.__name__
        state = StateModel(name=state_name, event_type=event_type, handler=handler, filters=filters)
        self.state_storage.add_state(state)

    def include_router(self, router: "StateRouter") -> None:
        self.routers.add(router)

    def default_handler_logic(
        self, handler_name: str, state_name: Optional[str] = None, filters: Tuple[Callable[[Any], bool]] = None
    ) -> Callable:
        def wrap(callback: Callable):
            self.registration_state_handler(handler_name, callback, state_name=state_name, filters=filters)
            return callback

        return wrap

    def message_handler(self, *filters: Callable[[Any], bool], state_name: Optional[str] = None) -> Callable:
        return self.default_handler_logic("message", state_name, filters)

    def callback_query_handler(self, *filters: Callable[[Any], bool], state_name: Optional[str] = None) -> Callable:
        return self.default_handler_logic("callback_query", state_name, filters)

    def edited_message_handler(self, *filters: Callable[[Any], bool], state_name: Optional[str] = None) -> Callable:
        return self.default_handler_logic("edited_message", state_name, filters)

    def channel_post_handler(self, *filters: Callable[[Any], bool], state_name: Optional[str] = None) -> Callable:
        return self.default_handler_logic("channel_post", state_name, filters)

    def edited_channel_post_handler(
        self, *filters: Callable[[Any], bool], state_name: Optional[str] = None
    ) -> Callable:
        return self.default_handler_logic("edited_channel_post", state_name, filters)


class MainStateRouter(StateRouter):
    def __init__(self, dispatcher: Optional[Dispatcher] = None) -> None:
        super().__init__()
        self.dispatcher = dispatcher or Dispatcher.get_current()

    def install_middleware(
        self,
        *,
        storage: Optional[Type[BaseStorage]] = None,
        default_state_name: Optional[str] = None,
        is_cached: bool = True
    ) -> None:
        self.dispatcher.middleware.setup(StateMiddleware(self, storage, default_state_name, is_cached))
