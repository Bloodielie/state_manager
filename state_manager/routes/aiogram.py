from logging import getLogger
from typing import Callable, Optional, Union, List, Set

from aiogram import Dispatcher, Bot

from state_manager.event_processors.aiogram import AiogramEventProcessor
from state_manager.models.state_managers.aiogram import AiogramStateManager
from state_manager.routes.base import BaseRouter, BaseMainRouter
from state_manager.routes.main import MainRouter, Router
from state_manager.storage_settings import StorageSettings
from state_manager.storages import redis
from state_manager.storages.base import BaseStorage
from state_manager.types.generals import Filters, StateNames, Filter

logger = getLogger(__name__)


class AiogramStateRouter(BaseRouter):
    def default_handler_logic(
        self,
        handler_name: str,
        filters: Filters,
        state_name: StateNames = None,
    ) -> Callable:
        def wrap(callback: Callable):
            self.registration_state_handler(handler_name, callback, state_name=state_name, filters=filters)
            return callback

        return wrap

    def message_handler(self, *filters: Filter, state_name: StateNames = None) -> Callable:
        return self.default_handler_logic("message", filters, state_name)

    def callback_query_handler(self, *filters: Filter, state_name: StateNames = None) -> Callable:
        return self.default_handler_logic("callback_query", filters, state_name)

    def edited_message_handler(self, *filters: Filter, state_name: StateNames = None) -> Callable:
        return self.default_handler_logic("edited_message", filters, state_name)

    def channel_post_handler(self, *filters: Filter, state_name: StateNames = None) -> Callable:
        return self.default_handler_logic("channel_post", filters, state_name)

    def edited_channel_post_handler(self, *filters: Filter, state_name: StateNames = None) -> Callable:
        return self.default_handler_logic("edited_channel_post", filters, state_name)


class AiogramMainStateRouter(AiogramStateRouter, BaseMainRouter):
    def __init__(
        self,
        dispatcher: Optional[Dispatcher] = None,
        routers: Optional[Union[List[BaseRouter], Set[BaseRouter]]] = None,
    ) -> None:
        super().__init__(routers=routers)
        self.dispatcher = dispatcher or Dispatcher.get_current()

    def install(
        self, *, storage: Optional[BaseStorage] = None, default_state_name: Optional[str] = None, is_cached: bool = True
    ) -> None:
        storage = storage or redis.RedisStorage(StorageSettings())
        self.container.bind_constant(BaseStorage, storage)
        self.container.bind_constant(Dispatcher, self.dispatcher)
        self.container.bind_constant(Bot, self.dispatcher.bot)

        logger.info(f"Install AiogramMainRouter")
        logger.debug(f"install, storage{storage}, default_state_name={default_state_name}, is_cached={is_cached}")
        AiogramEventProcessor.install(self.dispatcher, self.storage, storage, default_state_name, is_cached)


class AiogramRouter(Router):
    def __init__(self):
        super().__init__(mode="aiogram")


class AiogramMainRouter(MainRouter):
    def __init__(self, token: str):
        super().__init__(token, mode="aiogram")
