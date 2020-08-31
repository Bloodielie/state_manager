from logging import getLogger
from typing import Callable, Optional, Union, List, Set

from aiogram import Dispatcher, Bot, types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types.base import TelegramObject

from state_manager import BaseStateManager
from state_manager.dependency.container import AppContainer, ContainerWrapper
from state_manager.models.dependencys.aiogram import AiogramStateManager
from state_manager.storages.app import RouterStorage
from state_manager.routes.base import BaseRouter, BaseMainRouter
from state_manager.storage_settings import StorageSettings
from state_manager.storages import redis
from state_manager.storages.base import BaseStorage
from state_manager.types import aiogram_context, Filters, StateNames
from state_manager.utils.search import HandlerFinder
from state_manager.utils.utils import get_state_name

logger = getLogger(__name__)


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

    async def post_process_handlers(self, ctx: aiogram_context, event_type: str, data: Optional[dict] = None) -> None:
        container = AppContainer.get_current()
        dependency_container = ContainerWrapper(container)
        dependency_container.add_dependency(TelegramObject, ctx)
        dependency_container.add_dependency(dict, data)

        storage_ = container.get(BaseStorage)
        if storage_ is not None:
            dependency_container.add_dependency(
                BaseStateManager, AiogramStateManager(storage=storage_.implementation, context=ctx)
            )

        state_name = await self._get_user_state_name(ctx)
        return await self._handler_finder.get_handler_and_run(dependency_container, state_name, event_type)

    async def _get_user_state_name(self, ctx: aiogram_context) -> str:
        user_id = ctx.from_user.id
        return await get_state_name(user_id, self._storage, self._default_state_name)


class AiogramRouter(BaseRouter):
    def default_handler_logic(
        self,
        handler_name: str,
        filters: Filters,
        state_name: StateNames = None,
    ) -> Callable:
        def wrap(callback: Callable):
            self.registration_state_handler(handler_name, callback, state_name=state_name, filters=filters)
            return callback

        return wrap

    def message_handler(self, *filters: Filters, state_name: StateNames = None) -> Callable:
        filters: Filters
        return self.default_handler_logic("message", filters, state_name)

    def callback_query_handler(self, *filters: Filters, state_name: StateNames = None) -> Callable:
        filters: Filters
        return self.default_handler_logic("callback_query", filters, state_name)

    def edited_message_handler(self, *filters: Filters, state_name: StateNames = None) -> Callable:
        filters: Filters
        return self.default_handler_logic("edited_message", filters, state_name)

    def channel_post_handler(self, *filters: Filters, state_name: StateNames = None) -> Callable:
        filters: Filters
        return self.default_handler_logic("channel_post", filters, state_name)

    def edited_channel_post_handler(self, *filters: Filters, state_name: StateNames = None) -> Callable:
        filters: Filters
        return self.default_handler_logic("edited_channel_post", filters, state_name)


class AiogramMainRouter(AiogramRouter, BaseMainRouter):
    def __init__(
        self,
        dispatcher: Optional[Dispatcher] = None,
        routers: Optional[Union[List[BaseRouter], Set[BaseRouter]]] = None,
    ) -> None:
        super().__init__(routers=routers)
        self.dispatcher = dispatcher or Dispatcher.get_current()

    def install(
        self, *, storage: Optional[BaseStorage] = None, default_state_name: Optional[str] = None, is_cached: bool = True
    ) -> None:
        storage = storage or redis.RedisStorage(StorageSettings())
        self.container.bind_constant(BaseStorage, storage)
        self.container.bind_constant(Dispatcher, self.dispatcher)
        self.container.bind_constant(Bot, self.dispatcher.bot)

        logger.info(f"Install AiogramMainRouter")
        logger.debug(f"install, storage{storage}, default_state_name={default_state_name}, is_cached={is_cached}")
        self.dispatcher.middleware.setup(AiogramStateMiddleware(self.storage, storage, default_state_name, is_cached))
