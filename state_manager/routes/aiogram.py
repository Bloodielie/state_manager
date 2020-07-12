from typing import Callable, Optional, Type, Tuple, Any

from aiogram import Dispatcher

from state_manager.middlewares.aiogram import AiogramStateMiddleware
from state_manager.routes.base import BaseRouter
from state_manager.storage.base import BaseStorage
from logging import getLogger

logger = getLogger(__name__)


class AiogramRouter(BaseRouter):
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


class AiogramMainRouter(AiogramRouter):
    def __init__(self, dispatcher: Optional[Dispatcher] = None) -> None:
        super().__init__()
        self.dispatcher = dispatcher or Dispatcher.get_current()

    def install(
        self,
        *,
        storage: Optional[Type[BaseStorage]] = None,
        default_state_name: Optional[str] = None,
        is_cached: bool = True,
    ) -> None:
        logger.info(f"Install AiogramMainRouter")
        logger.debug(f"install, {storage=}, {default_state_name=}, {is_cached=}")
        self.dispatcher.middleware.setup(AiogramStateMiddleware(self, storage, default_state_name, is_cached))
