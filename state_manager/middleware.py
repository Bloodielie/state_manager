from asyncio import iscoroutinefunction
from functools import partial
from typing import Optional, Callable, Type

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from state_manager.models.dependency import DependencyManager
from state_manager.storage import redis
from state_manager.storage.base import BaseStorage
from state_manager.storage_settings import StorageSettings
from state_manager.types import Context
from state_manager.utils.dependency import get_func_attributes
from state_manager.utils.search import handler_search, search_handler_in_routes


# todo: add support other async lib for bots
class StateMiddleware(BaseMiddleware):
    def __init__(
        self,
        main_router: "MainStateRouter",
        *,
        storage: Optional[Type[BaseStorage]] = None,
        default_state_name: Optional[str] = None,
    ) -> None:
        self._main_router = main_router
        self._storage = storage or redis.RedisStorage(StorageSettings())
        self._default_state_name = default_state_name or "home"
        self._bot = main_router.dispatcher.bot
        super().__init__()

    async def on_post_process_message(self, message: types.Message, _, data: dict) -> None:
        if data:
            return
        await self.post_process_handlers(message, "message")

    async def on_post_process_callback_query(self, callback_query: types.CallbackQuery, _, data: dict) -> None:
        if data:
            return
        await self.post_process_handlers(callback_query, "callback_query")

    async def on_post_process_edited_message(self, callback_query: types.CallbackQuery, _, data: dict) -> None:
        if data:
            return
        await self.post_process_handlers(callback_query, "edited_message")

    async def post_process_handlers(self, ctx: Context, event_type: str) -> None:
        dependency = DependencyManager(
            bot=self._bot, dispatcher=self._main_router.dispatcher, context=ctx, storage=self._storage
        )
        if handler := await self._get_state_handler(dependency, event_type):
            func_attr = get_func_attributes(handler, dependency)

            if iscoroutinefunction(handler):
                await handler(**func_attr)
            else:
                handler(**func_attr)

    async def _get_state_handler(self, dependency_manager: DependencyManager, event_type: str) -> Optional[Callable]:
        state_name = await self._get_user_state_name(dependency_manager.context)
        handler_search_ = partial(handler_search, dependency_manager, event_type, state_name)
        if handler := handler_search_(self._main_router.state_storage):
            return handler
        if handler := search_handler_in_routes(self._main_router.routers, handler_search_):
            return handler

    async def _get_user_state_name(self, ctx: Context) -> str:
        user_id = ctx.from_user.id
        user_scene = await self._storage.get(user_id, self._default_state_name)
        if user_scene == self._default_state_name:
            await self._storage.put(user_id, self._default_state_name)
        return user_scene
