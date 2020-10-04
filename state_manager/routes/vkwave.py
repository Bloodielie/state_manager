from logging import getLogger
from typing import Callable, Optional, Union, List, Set, Any

from vkwave.bots import SimpleLongPollBot, TaskManager

from state_manager.event_processors.vkwave import VkWaveEventProcessor
from state_manager.handlers.vkwave import VkWaveStateHandler, VkWaveHandler
from state_manager.models.state_managers.vkwave import VkWaveStateManager
from state_manager.routes.base import BaseStateRouter, BaseMainStateRouter, BaseRouter, BaseMainRouter
from state_manager.storages import redis
from state_manager.storages.base import BaseStorage
from state_manager.storage_settings import StorageSettings
from state_manager.types.generals import StateNames, Filter

logger = getLogger(__name__)


class VkWaveStateRouter(BaseStateRouter):
    def message_handler(self, *filters: Filter, state_name: StateNames = None) -> Callable:

        def wrap(callback: Callable):
            self.registration_state_handler("message", callback, state_name=state_name, filters=filters)
            return callback

        return wrap


class VkWaveMainStateRouter(VkWaveStateRouter, BaseMainStateRouter):
    def __init__(
        self, bot: SimpleLongPollBot, routers: Optional[Union[List[BaseStateRouter], Set[BaseStateRouter]]] = None
    ) -> None:
        super().__init__(routers=routers)
        self.bot = bot

    def install(
        self,
        *,
        storage: Optional[BaseStorage] = None,
        default_state_name: Optional[str] = None
    ) -> None:
        logger.info(f"Install VkWaveMainRouter")
        logger.debug(f"install, storage={storage}, default_state_name={default_state_name}")
        self._default_state_name = default_state_name or "home"
        self._storage = storage or redis.RedisStorage(StorageSettings())

        self.container.bind_constant(BaseStorage, self._storage)
        self.container.bind_constant(SimpleLongPollBot, self.bot)

        VkWaveEventProcessor.install(self.bot, self._state_storage, storage, default_state_name)


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
        self.container.bind_constant(BaseStorage, storage)
        for class_, instance in self.inject_values.items():
            self.container.bind_constant(class_, instance)

        VkWaveEventProcessor.install(self.bot, self._state_storage, storage, default_state_name)

    def start(self) -> None:
        logger.info(f"start VkWaveMainRouter")
        self._task_manager.add_task(self.bot.run)
        self._task_manager.run(on_startup=self._events.on_startup, on_shutdown=self._events.on_shutdown)
