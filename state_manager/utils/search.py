from functools import partial
from logging import getLogger
from typing import Callable, Optional, Set, Dict, Tuple, Any, Union

from state_manager.filters.base import BaseFilter
from state_manager.models.dependencys.base import BaseDependencyStorage
from state_manager.routes.base import BaseRouter, BaseMainRouter
from state_manager.storages.state_storage import StateStorage
from state_manager.utils.check import check_function_and_run
from state_manager.utils.dependency import get_func_attributes

logger = getLogger(__name__)


class HandlerFinder:
    def __init__(self, main_router: BaseMainRouter, is_cache: bool = False) -> None:
        self._main_router = main_router
        self._is_cache = is_cache
        self._handler_in_cache: Dict[Tuple[str, str], Tuple[Callable, Callable]] = {}

    async def get_handler_and_run(self, dependency_storage: BaseDependencyStorage, state_name: str, event_type: str):
        handler = await self.get_state_handler(dependency_storage, state_name, event_type)
        if handler is None:
            return None
        func_attr = await get_func_attributes(handler, dependency_storage)
        return await check_function_and_run(handler, **func_attr)

    async def get_state_handler(
        self, dependency_storage: BaseDependencyStorage, state_name: str, event_type: str
    ) -> Optional[Callable]:
        if self._is_cache:
            logger.debug(f"Get state handler in cache, {state_name=}, {event_type=}, {dependency_storage=}")
            handler, filter = self._handler_in_cache.get((state_name, event_type), (None, None))
            if handler is not None and filter is None:
                return handler
            elif handler is None and filter is None:
                return await self._get_state_handler(dependency_storage, state_name, event_type)
            filter_result = await self._run_filter(filter, dependency_storage)
            if handler is not None and filter is not None and filter_result:
                return handler
            elif handler is not None and not filter:
                return None

        return await self._get_state_handler(dependency_storage, state_name, event_type)

    async def _get_state_handler(
        self, dependency_storage: BaseDependencyStorage, state_name: str, event_type: str
    ) -> Optional[Callable]:
        handler_search = partial(self._handler_search, dependency_storage, event_type, state_name)
        if handler := await handler_search(self._main_router.state_storage):
            return handler
        if handler := await self._search_handler_in_routes(self._main_router.routers, handler_search):
            return handler

    async def _handler_search(
        self, dependency_storage: BaseDependencyStorage, event_type: str, state_name: str, state_storage: StateStorage
    ) -> Optional[Callable]:
        states = state_storage.get_state(event_type, state_name)
        if states is None:
            return None
        for state in states:
            if state.filters is None:
                return state.handler
            for filter in state.filters:
                result = await self._run_filter(filter, dependency_storage)
                if not result:
                    continue
                if self._is_cache:
                    self._handler_in_cache[(state_name, event_type)] = (state.handler, filter)
                return state.handler

    @classmethod
    async def _search_handler_in_routes(cls, routes: Set[BaseRouter], search_func: Callable) -> Optional[Callable]:
        if not isinstance(routes, set):
            return None
        for router in routes:
            if handler := await search_func(router.state_storage):
                return handler
            if handler := await cls._search_handler_in_routes(router.routers, search_func):
                return handler

    async def _run_filter(self, filter: Union[Callable, BaseFilter], dependency_storage: BaseDependencyStorage) -> bool:
        if isinstance(filter, BaseFilter):
            filter_attr = await get_func_attributes(filter.check, dependency_storage)
            result = await check_function_and_run(filter.check, **filter_attr)
            return self.check_filter_result(result)
        else:
            filter_attr = await get_func_attributes(filter, dependency_storage)
            result = await check_function_and_run(filter, **filter_attr)
            return self.check_filter_result(result)

    @staticmethod
    def check_filter_result(filter_result: Any) -> bool:
        if isinstance(filter_result, bool):
            return filter_result
        logger.warning(f"Filter return no bool, {filter_result=}")
        return False
