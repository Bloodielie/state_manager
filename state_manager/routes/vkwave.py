from logging import getLogger
from typing import Callable, Optional, Union, List, Set

from vkwave.bots import SimpleLongPollBot

from state_manager.event_processors.vkwave import VkWaveEventProcessor
from state_manager.models.state_managers.vkwave import VkWaveStateManager
from state_manager.routes.base import BaseRouter, BaseMainRouter
from state_manager.routes.main import Router, MainRouter
from state_manager.storages import redis
from state_manager.storages.base import BaseStorage
from state_manager.storage_settings import StorageSettings
from state_manager.types.generals import Filters, StateNames, Filter

logger = getLogger(__name__)


class VkWaveStateRouter(BaseRouter):
    def message_handler(self, *filters: Filter, state_name: StateNames = None) -> Callable:
        filters: Filters

        def wrap(callback: Callable):
            self.registration_state_handler("message", callback, state_name=state_name, filters=filters)
            return callback

        return wrap


class VkWaveMainStateRouter(VkWaveStateRouter, BaseMainRouter):
    def __init__(
        self, bot: SimpleLongPollBot, routers: Optional[Union[List[BaseRouter], Set[BaseRouter]]] = None
    ) -> None:
        super().__init__(routers=routers)
        self.bot = bot

    def install(
        self,
        *,
        storage: Optional[BaseStorage] = None,
        default_state_name: Optional[str] = None,
        is_cached: bool = True,
    ) -> None:
        logger.info(f"Install VkWaveMainRouter")
        logger.debug(f"install, storage={storage}, default_state_name={default_state_name}, is_cached={is_cached}")
        self._default_state_name = default_state_name or "home"
        self._storage = storage or redis.RedisStorage(StorageSettings())

        self.container.bind_constant(BaseStorage, self._storage)
        self.container.bind_constant(SimpleLongPollBot, self.bot)

        VkWaveEventProcessor.install(self.bot, self.storage, storage, default_state_name, is_cached)


class VkWaveRouter(Router):
    def __init__(self):
        super().__init__(mode="vkwave")


class VkWaveMainRouter(MainRouter):
    def __init__(self, token: str):
        super().__init__(token, mode="vkwave")
