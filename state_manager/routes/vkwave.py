from logging import getLogger
from typing import Callable, Optional, Any, Union, List, Set

from vkwave.bots import SimpleLongPollBot, BotEvent, EventTypeFilter, BaseEvent
from vkwave.bots.addons.easy.base_easy_bot import SimpleBotEvent
from vkwave.types.bot_events import BotEventType

from state_manager import BaseStateManager
from state_manager.dependency.container import AppContainer, ContainerWrapper
from state_manager.models.dependencys.vkwave import VkWaveStateManager
from state_manager.routes.base import BaseRouter, BaseMainRouter
from state_manager.storages import redis
from state_manager.storages.base import BaseStorage
from state_manager.storage_settings import StorageSettings
from state_manager.utils.search import HandlerFinder
from state_manager.utils.utils import get_state_name

logger = getLogger(__name__)


class VkWaveRouter(BaseRouter):
    def message_handler(self, *filters: Callable[..., bool], state_name: Optional[str] = None) -> Callable:
        def wrap(callback: Callable):
            self.registration_state_handler("message", callback, state_name=state_name, filters=filters)
            return callback

        return wrap


class VkWaveMainRouter(VkWaveRouter, BaseMainRouter):
    def __init__(
        self, bot: Optional[SimpleLongPollBot], routers: Optional[Union[List[BaseRouter], Set[BaseRouter]]] = None
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
        logger.debug(f"install, {storage=}, {default_state_name=}, {is_cached=}")
        self._handler_finder = HandlerFinder(self.storage, is_cached)
        self._default_state_name = default_state_name or "home"

        self._storage = storage or redis.RedisStorage(StorageSettings())
        self.container.bind_constant(BaseStorage, self._storage)
        self.container.bind_constant(SimpleLongPollBot, self.bot)

        record = self.bot.router.registrar.new()
        record.filters.append(EventTypeFilter(BotEventType.MESSAGE_NEW))
        record.handle(self.bot.SimpleBotCallback(self._message_handler, self.bot.bot_type))
        self.bot.router.registrar.register(record.ready())

    async def _message_handler(self, event: BotEvent) -> Any:
        simple_event = SimpleBotEvent(event)

        container = AppContainer.get_current()
        dependency_container = ContainerWrapper(container)
        dependency_container.add_dependency(BaseEvent, simple_event)
        dependency_container.add_dependency(
            BaseStateManager, VkWaveStateManager(storage=container.get(BaseStorage).implementation, context=simple_event)
        )

        state_name = await self._get_state_name(simple_event)
        handler_result = await self._handler_finder.get_handler_and_run(dependency_container, state_name, "message")
        if handler_result is not None and isinstance(handler_result, str):
            await simple_event.answer(handler_result)

    async def _get_state_name(self, event: BotEvent) -> str:
        user_id = str(event.object.object.message.from_id)
        return await get_state_name(user_id, self._storage, self._default_state_name)
