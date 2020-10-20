from logging import getLogger
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.utils import executor

from state_manager import BaseStorage
from state_manager.event_processors.aiogram import AiogramEventProcessor
from state_manager.handlers.aiogram import AiogramStateHandler, AiogramHandler
from state_manager.routes.base.complete import BaseRouter, BaseMainRouter
from state_manager.storage_settings import StorageSettings
from state_manager.storages import redis

logger = getLogger(__name__)


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
        self.container.add_constant(BaseStorage, storage)
        for class_, instance in self.inject_values.items():
            self.container.add_constant(class_, instance)

        AiogramEventProcessor.install(self.dp, self._state_storage, storage, default_state_name)

    def start(self) -> None:
        logger.info(f"start AiogramMainRouter")
        executor.start_polling(
            self.dp,
            skip_updates=True,
            on_startup=self._events.on_startup,
            on_shutdown=self._events.on_shutdown
        )
