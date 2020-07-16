from logging import getLogger
from typing import Callable, Optional, Tuple, Union, List, Set

from aiogram import Dispatcher

from state_manager.middlewares.aiogram import AiogramStateMiddleware
from state_manager.routes.base import BaseRouter, BaseMainRouter
from state_manager.storage.base import BaseStorage

logger = getLogger(__name__)


class AiogramRouter(BaseRouter):
    def default_handler_logic(
        self, handler_name: str, filters: Optional[Tuple[Callable[..., bool], ...]], state_name: Optional[str] = None
    ) -> Callable:
        def wrap(callback: Callable):
            self.registration_state_handler(handler_name, callback, state_name=state_name, filters=filters)
            return callback

        return wrap

    def message_handler(self, *filters: Callable[..., bool], state_name: Optional[str] = None) -> Callable:
        return self.default_handler_logic("message", filters, state_name)

    def callback_query_handler(self, *filters: Callable[..., bool], state_name: Optional[str] = None) -> Callable:
        return self.default_handler_logic("callback_query", filters, state_name)

    def edited_message_handler(self, *filters: Callable[..., bool], state_name: Optional[str] = None) -> Callable:
        return self.default_handler_logic("edited_message", filters, state_name)

    def channel_post_handler(self, *filters: Callable[..., bool], state_name: Optional[str] = None) -> Callable:
        return self.default_handler_logic("channel_post", filters, state_name)

    def edited_channel_post_handler(self, *filters: Callable[..., bool], state_name: Optional[str] = None) -> Callable:
        return self.default_handler_logic("edited_channel_post", filters, state_name)


class AiogramMainRouter(AiogramRouter, BaseMainRouter):
    def __init__(
        self,
        dispatcher: Optional[Dispatcher] = None,
        routers: Optional[Union[List[BaseRouter], Set[BaseRouter]]] = None,
    ) -> None:
        super().__init__(routers=routers)
        self.dispatcher = dispatcher or Dispatcher.get_current()

    def install(
        self,
        *,
        storage: Optional[BaseStorage] = None,
        default_state_name: Optional[str] = None,
        is_cached: bool = True,
    ) -> None:
        logger.info(f"Install AiogramMainRouter")
        logger.debug(f"install, {storage=}, {default_state_name=}, {is_cached=}")
        self.dispatcher.middleware.setup(AiogramStateMiddleware(self, storage, default_state_name, is_cached))
