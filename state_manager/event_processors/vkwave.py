from logging import getLogger
from typing import Optional, Any, Callable

from vkwave.bots import BotEvent, SimpleLongPollBot, BaseEvent, EventTypeFilter
from vkwave.bots.addons.easy.base_easy_bot import SimpleBotEvent
from vkwave.types.bot_events import BotEventType

from state_manager import BaseStorage, BaseStateManager
from state_manager.dependency.container import AppContainer, ContainerWrapper
from state_manager.event_processors.base import BaseEventProcessor
from state_manager.models.state_managers.vkwave import VkWaveStateManager
from state_manager.storage_settings import StorageSettings
from state_manager.storages import redis
from state_manager.storages.app import RouterStorage
from state_manager.storages.state_storage import StateStorage
from state_manager.utils.search import get_state_handler_and_run
from state_manager.utils.utils import get_state_name

logger = getLogger(__name__)


class VkWaveEventProcessor(BaseEventProcessor):
    def __init__(
        self,
        state_storage: StateStorage,
        storage: Optional[BaseStorage] = None,
        default_state_name: Optional[str] = None,
    ) -> None:
        self._state_storage = state_storage
        self._storage = storage or redis.RedisStorage(StorageSettings())
        self._default_state_name = default_state_name or "home"

    @classmethod
    def install(
        cls,
        bot: SimpleLongPollBot,
        state_storage: StateStorage,
        storage: Optional[BaseStorage] = None,
        default_state_name: Optional[str] = None,
    ) -> None:
        self = cls(state_storage, storage, default_state_name)
        cls._install_handler(bot, self._message_handler, BotEventType.MESSAGE_NEW)

    @staticmethod
    def _install_handler(bot: SimpleLongPollBot, handler: Callable, event_type: BotEventType) -> None:
        record = bot.router.registrar.new()
        record.filters.append(EventTypeFilter(event_type))
        record.handle(bot.SimpleBotCallback(handler, bot.bot_type))
        bot.router.registrar.register(record.ready())

    async def _message_handler(self, event: BotEvent) -> Any:
        simple_event = SimpleBotEvent(event)

        container = AppContainer.get_current()
        dependency_container = ContainerWrapper(container)
        dependency_container.add_dependency(BaseEvent, simple_event)

        implementation_ = container.get(BaseStorage)
        if implementation_ is not None:
            dependency_container.add_dependency(
                BaseStateManager, VkWaveStateManager(storage=implementation_, context=simple_event)
            )

        state_name = await self._get_state_name(simple_event)
        handler_result = await get_state_handler_and_run(
            self._state_storage, dependency_container, state_name, "message"
        )
        if handler_result is not None and isinstance(handler_result, str):
            await simple_event.answer(handler_result)

    async def _get_state_name(self, event: BotEvent) -> str:
        user_id = str(event.object.object.message.from_id)
        return await get_state_name(user_id, self._storage, self._default_state_name)
