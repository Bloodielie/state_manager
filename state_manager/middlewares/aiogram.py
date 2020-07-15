from typing import Optional

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from state_manager.storage import redis
from state_manager.storage.base import BaseStorage
from state_manager.storage_settings import StorageSettings
from state_manager.types import Context
from state_manager.utils.dependency import dependency_storage_factory
from state_manager.utils.search import HandlerFinder
from state_manager.utils.utils import get_user_state_name


class AiogramStateMiddleware(BaseMiddleware):
    def __init__(
        self,
        main_router: "AiogramMainRouter",
        storage: Optional[BaseStorage] = None,
        default_state_name: Optional[str] = None,
        is_cached: bool = True,
    ) -> None:
        self._main_router = main_router
        self._handler_finder = HandlerFinder(main_router, is_cached)
        self._storage = storage or redis.RedisStorage(StorageSettings())
        self._default_state_name = default_state_name or "home"
        super().__init__()

    async def on_post_process_message(self, message: types.Message, _, data: dict) -> None:
        if data:
            return
        handler_result = await self.post_process_handlers(message, "message")
        if handler_result is not None and isinstance(handler_result, str):
            await message.answer(handler_result)

    async def on_post_process_callback_query(self, callback_query: types.CallbackQuery, _, data: dict) -> None:
        if data:
            return
        await self.post_process_handlers(callback_query, "callback_query")

    async def on_post_process_edited_message(self, callback_query: types.CallbackQuery, _, data: dict) -> None:
        if data:
            return
        await self.post_process_handlers(callback_query, "edited_message")

    async def post_process_handlers(self, ctx: Context, event_type: str) -> None:
        dependency_storage = dependency_storage_factory(
            bot=self._main_router.dispatcher.bot,
            dispatcher=self._main_router.dispatcher,
            context=ctx,
            storage=self._storage,
        )
        state_name = await self._get_user_state_name(ctx)
        return await self._handler_finder.get_handler_and_run(dependency_storage, state_name, event_type)

    async def _get_user_state_name(self, ctx: Context) -> str:
        user_id = ctx.from_user.id
        return await get_user_state_name(user_id, self._storage, self._default_state_name)
