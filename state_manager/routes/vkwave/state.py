from logging import getLogger
from typing import Callable, Optional, Union, List, Set

from vkwave.bots import SimpleLongPollBot

from state_manager import BaseStorage
from state_manager.event_processors.vkwave import VkWaveEventProcessor
from state_manager.routes.base.state import BaseStateRouter, BaseMainStateRouter
from state_manager.storage_settings import StorageSettings
from state_manager.storages import redis
from state_manager.types.generals import Filter, StateNames

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

        self.container.add_constant(BaseStorage, self._storage)
        self.container.add_constant(SimpleLongPollBot, self.bot)

        VkWaveEventProcessor.install(self.bot, self.container, self._state_storage, storage, default_state_name)
