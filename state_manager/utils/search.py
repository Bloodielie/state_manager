from functools import partial
from logging import getLogger
from typing import Callable, Optional, Set, Dict, Tuple, Union, Any

from state_manager.dependency.container import ContainerWrapper
from state_manager.dependency.dependency import get_func_attributes
from state_manager.filters.base import BaseFilter
from state_manager.models.routers_storage import RouterStorage
from state_manager.routes.base import BaseRouter
from state_manager.storages.state_storage import StateStorage
from state_manager.utils.check import check_function_and_run, check_filter_result

logger = getLogger(__name__)


async def run_filter(
    filter_: Union[Callable[..., Any], BaseFilter], dependency_storage: ContainerWrapper,
) -> bool:
    if isinstance(filter_, BaseFilter):
        filter_attr = await get_func_attributes(filter_.check, dependency_storage)
        return check_filter_result(await check_function_and_run(filter_.check, **filter_attr))

    filter_attr = await get_func_attributes(filter_, dependency_storage)
    return check_filter_result(await check_function_and_run(filter_, **filter_attr))


class HandlerFinder:
    def __init__(self, router_storage: RouterStorage, is_cache: bool = False) -> None:
        self.router_storage = router_storage
        self._is_cache = is_cache
        self._handler_in_cache: Dict[Tuple[str, str], Tuple[Callable, Callable]] = {}

    async def get_handler_and_run(self, dependency_storage: ContainerWrapper, state_name: str, event_type: str):
        callback = await self.get_state_callback(dependency_storage, state_name, event_type)
        if callback is None:
            return None
        func_attr = await get_func_attributes(callback, dependency_storage)
        return await check_function_and_run(callback, **func_attr)

    async def get_state_callback(
        self, dependency_storage: ContainerWrapper, state_name: str, event_type: str,
    ) -> Optional[Callable]:
        if self._is_cache:
            logger.debug(f"Get state handler in cache, state_name={state_name}, event_type={event_type}, dependency_storage={dependency_storage}")
            callback, filter_ = self._handler_in_cache.get((state_name, event_type), (None, None))
            if callback is not None and filter_ is None:
                return callback
            elif callback is None and filter_ is None:
                return await self._get_state_callback(dependency_storage, state_name, event_type)
            filter_result = await run_filter(filter_, dependency_storage)  # type: ignore
            if callback is not None and filter_ is not None and filter_result:
                return callback
        else:
            return await self._get_state_callback(dependency_storage, state_name, event_type)

    async def _get_state_callback(
        self, dependency_storage: ContainerWrapper, state_name: str, event_type: str,
    ) -> Optional[Callable]:
        handler_search = partial(self._callback_search, dependency_storage, event_type, state_name)
        callback = await handler_search(self.router_storage.state_storage)
        if callback:
            return callback
        callback = await self._search_callback_in_routes(self.router_storage.routers, handler_search)
        if callback:
            return callback

    async def _callback_search(
        self, dependency_storage: ContainerWrapper, event_type: str, state_name: str, state_storage: StateStorage,
    ) -> Optional[Callable]:
        states = state_storage.get_state(event_type, state_name)
        if states is None:
            return None
        for state in states:
            if state.filters is None:
                return state.handler
            for filter_ in state.filters:
                filter_result = await run_filter(filter_, dependency_storage)
                if not filter_result:
                    continue
                if self._is_cache:
                    self._handler_in_cache[(state_name, event_type)] = (state.handler, filter_)
                return state.handler

    @classmethod
    async def _search_callback_in_routes(cls, routes: Set[BaseRouter], search_func: Callable) -> Optional[Callable]:
        if not isinstance(routes, set):
            return None
        for router in routes:
            callback = await search_func(router.storage.state_storage)
            if callback:
                return callback
            callback = await cls._search_callback_in_routes(router.storage.routers, search_func)
            if callback:
                return callback
