from logging import getLogger
from typing import Callable, Optional, Any

from vkwave.bots import SimpleLongPollBot, BotEvent, EventTypeFilter
from vkwave.bots.addons.easy.base_easy_bot import SimpleBotEvent
from vkwave.types.bot_events import BotEventType

from state_manager.routes.base import BaseRouter, BaseMainRouter
from state_manager.storage import redis
from state_manager.storage.base import BaseStorage
from state_manager.storage_settings import StorageSettings
from state_manager.utils.dependency import dependency_storage_factory
from state_manager.utils.search import HandlerFinder
from state_manager.utils.utils import get_user_state_name

logger = getLogger(__name__)


class VkWaveRouter(BaseRouter):
    def message_handler(self, *filters: Callable[..., bool], state_name: Optional[str] = None) -> Callable:
        def wrap(callback: Callable):
            self.registration_state_handler("message", callback, state_name=state_name, filters=filters)
            return callback

        return wrap


class VkWaveMainRouter(VkWaveRouter, BaseMainRouter):
    def __init__(self, bot: Optional[SimpleLongPollBot]) -> None:
        super().__init__()
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
        self._handler_finder = HandlerFinder(self, is_cached)
        self._storage = storage or redis.RedisStorage(StorageSettings())
        self._default_state_name = default_state_name or "home"

        record = self.bot.router.registrar.new()
        record.filters.append(EventTypeFilter(BotEventType.MESSAGE_NEW))
        record.handle(self.bot.SimpleBotCallback(self._message_handler, self.bot.bot_type))
        self.bot.router.registrar.register(record.ready())

    async def _message_handler(self, event: BotEvent) -> Any:
        event = SimpleBotEvent(event)
        dependency_storage = dependency_storage_factory(
            lib="vkwave", bot=self.bot, context=event, storage=self._storage,
        )
        state_name = await self._get_user_state_name(event)
        handler_result = await self._handler_finder.get_handler_and_run(dependency_storage, state_name, "message")
        if handler_result is not None and isinstance(handler_result, str):
            await event.answer(handler_result)

    async def _get_user_state_name(self, event: BotEvent) -> str:
        user_id = str(event.object.object.message.from_id)
        return await get_user_state_name(user_id, self._storage, self._default_state_name)
