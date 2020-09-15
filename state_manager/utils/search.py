from functools import partial
from logging import getLogger
from typing import Callable, Optional, Set, Dict, Tuple, List, Union, Any

from state_manager.dependency.container import ContainerWrapper
from state_manager.dependency.dependency import get_func_attributes
from state_manager.filters.base import BaseFilter
from state_manager.storages.app import RouterStorage, HandlerStorage
from state_manager.routes.base import BaseRouter
from state_manager.storages.state_storage import StateStorage
from state_manager.utils.check import check_filter_result
from state_manager.utils.runers import check_function_and_run

logger = getLogger(__name__)

all_state_name = "*"


async def run_filter(filter_: Union[Callable[..., Any], BaseFilter], dependency_storage: ContainerWrapper,) -> bool:
    if isinstance(filter_, BaseFilter):
        filter_attr = await get_func_attributes(filter_.check, dependency_storage)
        return check_filter_result(await check_function_and_run(filter_.check, **filter_attr))

    filter_attr = await get_func_attributes(filter_, dependency_storage)
    return check_filter_result(await check_function_and_run(filter_, **filter_attr))


async def get_state_handler(
    state_storage: StateStorage, dependency_container: ContainerWrapper, state_name: str, event_type: str,
):
    for state_model in state_storage.get_state(event_type, [all_state_name, state_name]):
        if state_model.filters is None:
            return state_model.handler

        for filter_ in state_model.filters:
            filter_result = await run_filter(filter_, dependency_container)
            if filter_result:
                return state_model.handler


async def get_state_handler_and_run(
    state_storage: StateStorage, dependency_container: ContainerWrapper, state_name: str, event_type: str
):
    callback = await get_state_handler(state_storage, dependency_container, state_name, event_type)
    if callback is not None:
        func_attr = await get_func_attributes(callback, dependency_container)
        return await check_function_and_run(callback, **func_attr)


async def _find_handler_in_storages(handler_storages, dependency_storage, callback_search_func):
    for handler_storage in handler_storages:
        if handler_storage.handler is not None and handler_storage.filters is None:
            return handler_storage.handler
        elif handler_storage.handler is None and handler_storage.filters is None:
            return await callback_search_func()

        for filter_ in handler_storage.filters:
            filter_result = await run_filter(filter_, dependency_storage)
            if handler_storage.handler is not None and filter_ is not None and filter_result:
                return handler_storage.handler
        return await callback_search_func()


class HandlerFinder:
    def __init__(self, router_storage: RouterStorage, is_cache: bool = False) -> None:
        self.router_storage = router_storage
        self._is_cache = is_cache
        self._handler_in_cache: Dict[Tuple[str, str], List[HandlerStorage]] = {}

    async def get_handler_and_run(self, dependency_storage: ContainerWrapper, state_name: str, event_type: str):
        callback = await self.get_state_callback(dependency_storage, state_name, event_type)
        if callback is None:
            return None
        func_attr = await get_func_attributes(callback, dependency_storage)
        return await check_function_and_run(callback, **func_attr)

    async def get_state_callback(
        self, dependency_storage: ContainerWrapper, state_name: str, event_type: str,
    ) -> Optional[Callable]:
        handler_storages = self._handler_in_cache.get((all_state_name, event_type), None)
        if handler_storages is not None:
            callback_search_func = partial(self._get_state_callback, dependency_storage, all_state_name, event_type)
            all_state_result = await _find_handler_in_storages(
                handler_storages, dependency_storage, callback_search_func
            )
        else:
            all_state_result = await self._get_state_callback(dependency_storage, all_state_name, event_type)
        if all_state_result is not None:
            return all_state_result

        if self._is_cache:
            logger.debug(
                f"Get state handler in cache, state_name={state_name}, event_type={event_type}, dependency_storage={dependency_storage}"
            )
            handler_storages = self._handler_in_cache.get((state_name, event_type), None)
            if handler_storages is None:
                return await self._get_state_callback(dependency_storage, state_name, event_type)

            callback_search_func = partial(self._get_state_callback, dependency_storage, state_name, event_type)
            return await _find_handler_in_storages(handler_storages, dependency_storage, callback_search_func)
        else:
            return await self._get_state_callback(dependency_storage, state_name, event_type)

    async def _get_state_callback(
        self, dependency_storage: ContainerWrapper, state_name: str, event_type: str,
    ) -> Optional[Callable]:
        handler_search = partial(self._search_callback, dependency_storage, event_type, state_name)

        callback = await handler_search(self.router_storage.state_storage)
        if callback:
            return callback
        callback = await self._search_callback_in_routes(self.router_storage.routers, handler_search)
        if callback:
            return callback

    async def _search_callback(
        self, dependency_storage: ContainerWrapper, event_type: str, state_name: str, state_storage: StateStorage,
    ) -> Optional[Callable]:
        """Finding the state passing all filters"""
        result = None
        for state in state_storage.get_state(event_type, state_name):
            if state.filters is None:
                result = HandlerStorage(handler=state.handler, filters=None)
                break
            for filter_ in state.filters:
                filter_result = await run_filter(filter_, dependency_storage)
                if not filter_result:
                    continue
                result = HandlerStorage(handler=state.handler, filters=state.filters)
                break

        if result is not None:
            if self._is_cache:
                value_in_cache = self._handler_in_cache.get((state_name, event_type))
                if value_in_cache is None:
                    self._handler_in_cache[(state_name, event_type)] = [result]
                else:
                    value_in_cache.append(result)
            return result.handler

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
