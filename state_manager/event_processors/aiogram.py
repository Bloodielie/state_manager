from typing import Optional

from aiogram import Dispatcher
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from aiogram.types.base import TelegramObject

from state_manager import BaseStorage, BaseStateManager
from pyject import DependencyNotFound
from state_manager.event_processors.base import BaseEventProcessor
from state_manager.models.state_managers.aiogram import AiogramStateManager
from state_manager.storage_settings import StorageSettings
from state_manager.storages import redis
from state_manager.storages.state_storage import StateStorage
from state_manager.types.aiogram import aiogram_context
from state_manager.types.generals import BaseContainer
from state_manager.utils.search import get_state_handler_and_run
from state_manager.utils.utils import get_state_name


class AiogramEventProcessor(BaseEventProcessor, BaseMiddleware):
    def __init__(
        self,
        state_storage: StateStorage,
        container: BaseContainer,
        state_data_storage: Optional[BaseStorage] = None,
        default_state_name: Optional[str] = None,
    ) -> None:
        self._state_storage = state_storage

        self._state_data_storage = state_data_storage or redis.RedisStorage(StorageSettings())
        self._default_state_name = default_state_name or "home"
        self._container = container
        super().__init__()

    async def on_post_process_message(self, message: Message, _, data: dict) -> None:
        if data.get("state") or data.get("raw_state") or data.get("command"):
            return
        handler_result = await self.post_process_handlers(message, "message", data)
        if handler_result is not None and isinstance(handler_result, str):
            await message.answer(handler_result)

    async def on_post_process_callback_query(self, callback_query: CallbackQuery, _, data: dict) -> None:
        if data.get("state") or data.get("raw_state") or data.get("command"):
            return
        await self.post_process_handlers(callback_query, "callback_query", data)

    async def on_post_process_edited_message(self, callback_query: CallbackQuery, _, data: dict) -> None:
        if data.get("state") or data.get("raw_state") or data.get("command"):
            return
        await self.post_process_handlers(callback_query, "edited_message", data)

    async def post_process_handlers(self, ctx: aiogram_context, event_type: str, data: Optional[dict] = None) -> None:
        self._container.add_context(TelegramObject, ctx)

        if data is not None:
            for value in data.values():
                self._container.add_context(value.__class__, value)

        try:
            implementation_ = self._container.get(BaseStorage)
            state_manager = AiogramStateManager(storage=implementation_, context=ctx)
            self._container.add_context(BaseStateManager, state_manager)
        except DependencyNotFound:
            pass

        state_name = await self._get_user_state_name(ctx)
        return await get_state_handler_and_run(self._state_storage, self._container, state_name, event_type)

    @classmethod
    def install(
        cls,
        dispatcher: Dispatcher,
        state_storage: StateStorage,
        container: BaseContainer,
        state_data_storage: Optional[BaseStorage] = None,
        default_state_name: Optional[str] = None,
    ) -> None:
        dispatcher.middleware.setup(cls(state_storage, container, state_data_storage, default_state_name))

    async def _get_user_state_name(self, ctx: aiogram_context) -> str:
        user_id = ctx.from_user.id
        return await get_state_name(user_id, self._state_data_storage, self._default_state_name)
