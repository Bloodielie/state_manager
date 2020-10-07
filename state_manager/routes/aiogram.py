from logging import getLogger
from typing import Callable, Optional, Union, List, Set

from aiogram import Dispatcher, Bot
from aiogram.utils import executor

from state_manager.event_processors.aiogram import AiogramEventProcessor
from state_manager.handlers.aiogram import AiogramStateHandler, AiogramHandler
from state_manager.models.state_managers.aiogram import AiogramStateManager
from state_manager.routes.base import BaseStateRouter, BaseMainStateRouter, BaseRouter, BaseMainRouter
from state_manager.storage_settings import StorageSettings
from state_manager.storages import redis
from state_manager.storages.base import BaseStorage
from state_manager.types.generals import Filters, StateNames, Filter

logger = getLogger(__name__)


class AiogramStateRouter(BaseStateRouter):
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


class AiogramMainStateRouter(AiogramStateRouter, BaseMainStateRouter):
    def __init__(
        self,
        dispatcher: Optional[Dispatcher] = None,
        routers: Optional[Union[List[BaseStateRouter], Set[BaseStateRouter]]] = None,
    ) -> None:
        super().__init__(routers=routers)
        self.dispatcher = dispatcher or Dispatcher.get_current()

    def install(
        self, *, storage: Optional[BaseStorage] = None, default_state_name: Optional[str] = None
    ) -> None:
        storage = storage or redis.RedisStorage(StorageSettings())
        self.container.bind_constant(BaseStorage, storage)
        self.container.bind_constant(Dispatcher, self.dispatcher)
        self.container.bind_constant(Bot, self.dispatcher.bot)

        logger.info(f"Install AiogramMainRouter")
        logger.debug(f"install, storage{storage}, default_state_name={default_state_name}")
        AiogramEventProcessor.install(self.dispatcher, self._state_storage, storage, default_state_name)


class AiogramRouter(BaseRouter):
    def __init__(self):
        super().__init__()
        self.on_state = AiogramStateHandler(self._state_storage)
        self.on = AiogramHandler(self._state_storage)


class AiogramMainRouter(BaseMainRouter, AiogramRouter):
    def __init__(self, token: str):
        super().__init__(token=token)
        bot = Bot(token=token)
        self.dp = Dispatcher(bot)
        self.inject_values = {Bot: bot, Dispatcher: self.dp}

    def install(
        self, *, storage: Optional[BaseStorage] = None, default_state_name: Optional[str] = None
    ) -> None:
        logger.info(f"install AiogramMainRouter")
        storage = storage or redis.RedisStorage(StorageSettings())
        self.container.bind_constant(BaseStorage, storage)
        for class_, instance in self.inject_values.items():
            self.container.bind_constant(class_, instance)

        AiogramEventProcessor.install(self.dp, self._state_storage, storage, default_state_name)

    def start(self) -> None:
        logger.info(f"start AiogramMainRouter")
        executor.start_polling(
            self.dp,
            skip_updates=True,
            on_startup=self._events.on_startup,
            on_shutdown=self._events.on_shutdown
        )
