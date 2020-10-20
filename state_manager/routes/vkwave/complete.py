from logging import getLogger
from typing import Optional

from vkwave.bots import TaskManager, SimpleLongPollBot

from state_manager import BaseStorage
from state_manager.event_processors.vkwave import VkWaveEventProcessor
from state_manager.handlers.vkwave import VkWaveStateHandler, VkWaveHandler
from state_manager.routes.base.complete import BaseRouter, BaseMainRouter
from state_manager.storage_settings import StorageSettings
from state_manager.storages import redis

logger = getLogger(__name__)


class VkWaveRouter(BaseRouter):
    def __init__(self):
        super().__init__()
        self.on_state = VkWaveStateHandler(self._state_storage)
        self.on = VkWaveHandler(self._state_storage)


class VkWaveMainRouter(BaseMainRouter, VkWaveRouter):
    def __init__(self, token: str, group_id: int):
        super().__init__(token=token)
        self.group_id = group_id
        self._task_manager = TaskManager()
        self.bot = SimpleLongPollBot(tokens=token, group_id=group_id)
        self.inject_values = {SimpleLongPollBot: self.bot}

    def install(
        self, *, storage: Optional[BaseStorage] = None, default_state_name: Optional[str] = None
    ) -> None:
        logger.info(f"install VkWaveMainRouter")
        storage = storage or redis.RedisStorage(StorageSettings())
        self.container.add_constant(BaseStorage, storage)
        for class_, instance in self.inject_values.items():
            self.container.add_constant(class_, instance)

        VkWaveEventProcessor.install(self.bot, self._state_storage, storage, default_state_name)

    def start(self) -> None:
        logger.info(f"start VkWaveMainRouter")
        self._task_manager.add_task(self.bot.run)
        self._task_manager.run(on_startup=self._events.on_startup, on_shutdown=self._events.on_shutdown)
