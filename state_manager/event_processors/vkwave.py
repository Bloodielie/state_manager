from logging import getLogger
from typing import Optional, Any, Callable

from vkwave.bots import BotEvent, SimpleLongPollBot, BaseEvent, EventTypeFilter
from vkwave.bots.addons.easy.base_easy_bot import SimpleBotEvent
from vkwave.types.bot_events import BotEventType

from state_manager import BaseStorage, BaseStateManager
from pyject import Container
from pyject import DependencyNotFound
from state_manager.event_processors.base import BaseEventProcessor
from state_manager.models.state_managers.vkwave import VkWaveStateManager
from state_manager.storage_settings import StorageSettings
from state_manager.storages import redis
from state_manager.storages.app import RouterStorage
from state_manager.storages.state_storage import StateStorage
from state_manager.types.generals import BaseContainer
from state_manager.utils.search import get_state_handler_and_run
from state_manager.utils.utils import get_state_name

logger = getLogger(__name__)


class VkWaveEventProcessor(BaseEventProcessor):
    def __init__(
        self,
        state_storage: StateStorage,
        container: BaseContainer,
        storage: Optional[BaseStorage] = None,
        default_state_name: Optional[str] = None,
    ) -> None:
        self._state_storage = state_storage
        self._storage = storage or redis.RedisStorage(StorageSettings())
        self._default_state_name = default_state_name or "home"
        self._container = container

    @classmethod
    def install(
        cls,
        bot: SimpleLongPollBot,
        state_storage: StateStorage,
        container: BaseContainer,
        storage: Optional[BaseStorage] = None,
        default_state_name: Optional[str] = None,
    ) -> None:
        self = cls(state_storage, container, storage, default_state_name)
        cls._install_handler(bot, self._message_handler, BotEventType.MESSAGE_NEW)

    @staticmethod
    def _install_handler(bot: SimpleLongPollBot, handler: Callable, event_type: BotEventType) -> None:
        record = bot.router.registrar.new()
        record.filters.append(EventTypeFilter(event_type))
        record.handle(bot.SimpleBotCallback(handler, bot.bot_type))
        bot.router.registrar.register(record.ready())

    async def _message_handler(self, event: BotEvent) -> Any:
        simple_event = SimpleBotEvent(event)

        self._container.add_context(BaseEvent, simple_event)

        try:
            implementation_ = self._container.get(BaseStorage)
            self._container.add_context(BaseStateManager, VkWaveStateManager(storage=implementation_, context=simple_event))
        except DependencyNotFound:
            pass

        state_name = await self._get_state_name(simple_event)
        handler_result = await get_state_handler_and_run(
            self._state_storage, self._container, state_name, "message"
        )
        if handler_result is not None and isinstance(handler_result, str):
            await simple_event.answer(handler_result)

    async def _get_state_name(self, event: BotEvent) -> str:
        user_id = str(event.object.object.message.from_id)
        return await get_state_name(user_id, self._storage, self._default_state_name)
