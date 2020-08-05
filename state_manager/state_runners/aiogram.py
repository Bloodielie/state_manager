from typing import Optional

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types.base import TelegramObject

from state_manager import BaseStateManager
from state_manager.dependency.container import AppContainer, ContainerWrapper
from state_manager.models.dependencys.aiogram import AiogramStateManager
from state_manager.models.routers_storage import RouterStorage
from state_manager.storage_settings import StorageSettings
from state_manager.storages import redis
from state_manager.storages.base import BaseStorage
from state_manager.types import Context
from state_manager.utils.search import HandlerFinder
from state_manager.utils.utils import get_state_name


class AiogramStateMiddleware(BaseMiddleware):
    def __init__(
        self,
        router_storage: RouterStorage,
        storage: Optional[BaseStorage] = None,
        default_state_name: Optional[str] = None,
        is_cached: bool = True,
    ) -> None:
        self._handler_finder = HandlerFinder(router_storage, is_cached)
        self._storage = storage or redis.RedisStorage(StorageSettings())
        self._default_state_name = default_state_name or "home"
        super().__init__()

    async def on_post_process_message(self, message: types.Message, _, data: dict) -> None:
        if data.get("state") or data.get("raw_state") or data.get("command"):
            return
        handler_result = await self.post_process_handlers(message, "message", data)
        if handler_result is not None and isinstance(handler_result, str):
            await message.answer(handler_result)

    async def on_post_process_callback_query(self, callback_query: types.CallbackQuery, _, data: dict) -> None:
        if data.get("state") or data.get("raw_state") or data.get("command"):
            return
        await self.post_process_handlers(callback_query, "callback_query", data)

    async def on_post_process_edited_message(self, callback_query: types.CallbackQuery, _, data: dict) -> None:
        if data.get("state") or data.get("raw_state") or data.get("command"):
            return
        await self.post_process_handlers(callback_query, "edited_message", data)

    async def post_process_handlers(self, ctx: Context, event_type: str, data: Optional[dict] = None) -> None:
        container = AppContainer.get_current()
        dependency_container = ContainerWrapper(container)
        dependency_container.add_dependency(TelegramObject, ctx)
        dependency_container.add_dependency(dict, data)
        dependency_container.add_dependency(
            BaseStateManager, AiogramStateManager(storage=container.get(BaseStorage).implementation, context=ctx)
        )

        state_name = await self._get_user_state_name(ctx)
        return await self._handler_finder.get_handler_and_run(dependency_container, state_name, event_type)

    async def _get_user_state_name(self, ctx: Context) -> str:
        user_id = ctx.from_user.id
        return await get_state_name(user_id, self._storage, self._default_state_name)
